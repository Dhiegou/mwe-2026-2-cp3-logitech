# 2. Arquitetura

## Diagrama dos serviços

Toda seta indica o protocolo. As setas AMQP passam pelo broker RabbitMQ (filas duráveis), que
aparece no compose ao final do documento.

```mermaid
flowchart LR
    VEI(["Rastreador do veículo"]) -->|"UDP: posição a cada 30 s"| TEL["Telemetria"]
    APP(["App do motorista"]) -->|"HTTPS: confirmação de entrega e registro de ausência"| PED["Pedidos (Java)"]
    PED -->|"AMQP: EntregaConfirmada"| GAR["Garantia de Prazo (Python, novo)"]
    GAR -->|"HTTP: prazo prometido e valor do frete"| FRE["Frete (Python)"]
    GAR -->|"HTTP: comprovação de ausência"| TEL
    GAR -->|"AMQP: CreditoConcedido"| FAT["Faturamento (C#)"]
    GAR -->|"AMQP: AtrasoApurado"| NOT["Notificações (Node/TypeScript)"]
    NOT -->|"HTTPS: API atual"| EMA(["Serviço de e-mail atual"])
    NOT -->|"HTTPS: API do parceiro"| WPP(["Parceiro WhatsApp"])
    NOT -->|"AMQP: falha definitiva"| DLQ[("Fila de falhas")]
    TEL -->|"AMQP: PosicaoAtualizada"| ACO["API de Acompanhamento (Node/TypeScript)"]
    PED -->|"AMQP: situação do pedido"| ACO
    GAR -->|"AMQP: AtrasoApurado"| ACO
    FAT -->|"AMQP: NotaDeCreditoEmitida"| ACO
    POR["Portal do Cliente (React)"] -->|"HTTP: carga inicial"| ACO
    ACO -->|"SSE: atualizações ao vivo"| POR
```

### Fluxo do crédito e o prazo de 5 minutos (RNF02)

1. O app do motorista envia a confirmação ao Pedidos por HTTPS e só considera enviada quando
   recebe a resposta `201`.
2. O Pedidos grava a confirmação e o evento `EntregaConfirmada` na mesma transação (outbox), e
   um publicador envia o evento ao RabbitMQ em poucos segundos.
3. A Garantia de Prazo consome o evento, consulta o Frete (e a Telemetria, se houve ausência
   registrada), calcula o crédito e grava o resultado e os eventos `CreditoConcedido` e
   `AtrasoApurado` na mesma transação (outbox).
4. O Faturamento consome `CreditoConcedido`, emite a nota de crédito e publica
   `NotaDeCreditoEmitida`, que atualiza o saldo no Portal.

Em operação normal o fluxo leva segundos. As chamadas HTTP da Garantia têm timeout de 2 s e até
3 tentativas; se o Frete ou a Telemetria estiverem fora, a mensagem volta para a fila com espera,
e um alerta dispara quando a mensagem mais antiga da fila passa de 3 min, antes de estourar os
5 min do RNF02.

## Protocolo de cada comunicação

| Origem | Destino | Protocolo | Requisito atendido | Justificativa |
|---|---|---|---|---|
| Rastreador do veículo | Telemetria | UDP | RNF01, RF10 | A posição chega a cada 30 s e a perda é tolerada: um pacote perdido é substituído pelo próximo, 30 s depois, e retransmitir posição velha não tem valor. Sem conexão nem retransmissão, o custo por veículo é mínimo. Pacote fora de ordem é descartado pelo horário de medição |
| App do motorista | Pedidos | HTTPS (HTTP sobre TCP) com cabeçalho `Idempotency-Key` | RNF01, RF09 | A confirmação de entrega não tolera perda: o TCP garante a entrega e a resposta `201` é o recibo. Sem recibo (sinal fraco), o app reenvia com a mesma chave (o id da confirmação) e o Pedidos devolve a mesma resposta, sem registrar de novo |
| App do motorista | Pedidos | HTTPS (HTTP sobre TCP) | RF05 | O registro de ausência marca o horário usado na comprovação, então também precisa de recibo |
| Pedidos | Garantia de Prazo | AMQP (sobre TCP) via RabbitMQ: fila durável, mensagem persistente, ack manual depois do commit | RNF01, RNF02, RF09 | `EntregaConfirmada` fica gravada no broker até a Garantia confirmar o processamento, então não se perde nem com a Garantia fora do ar. O processamento assíncrono cabe com folga nos 5 min. A entrega é "pelo menos uma vez", por isso o consumidor é idempotente |
| Garantia de Prazo | Frete | HTTP (REST, `GET /fretes/{pedidoId}`) | RF01, RF02 | A Garantia precisa do prazo prometido e do valor do frete no momento do cálculo. É uma consulta de leitura, síncrona e idempotente, que pode ser repetida com timeout curto dentro da janela do RNF02 |
| Garantia de Prazo | Telemetria | HTTP (REST, `GET /veiculos/{veiculoId}/comprovacao-ausencia`) | RF05 | Só acontece quando houve ausência registrada. A decisão do crédito depende da resposta (comprovada ou não), por isso a chamada é síncrona; é leitura idempotente |
| Garantia de Prazo | Faturamento | AMQP via RabbitMQ (persistente) | RF06, RNF02 | `CreditoConcedido` não pode se perder, porque é dinheiro do cliente. O Faturamento emite a nota no seu ritmo e a fila absorve picos; a idempotência fica no id do crédito |
| Garantia de Prazo | Notificações | AMQP via RabbitMQ (persistente) | RF03, RF07 | `AtrasoApurado` é publicado em toda apuração, com o atraso, o crédito (ou o motivo de não haver crédito) e a indicação de aviso. Quando o atraso passa da tolerância, Notificações avisa o cliente, inclusive o Cortesia, que não tem crédito. A fila desacopla a Garantia da disponibilidade dos canais de envio |
| Notificações | Serviço de e-mail atual | HTTPS (API atual) | RF07, RF08 | Mantém o serviço que já existe. Timeout ou erro 5xx conta como falha e dispara a retentativa |
| Notificações | Parceiro WhatsApp | HTTPS (API do parceiro, via adaptador) | RF07, RF08 | A API do parceiro tem outro formato e o adaptador traduz a mensagem. As falhas seguem a mesma política de retentativa |
| Notificações | Fila de falhas (RabbitMQ) | AMQP (fila durável) | RF08 | Depois da 3ª retentativa, a notificação vai para a fila de falhas e gera alerta: nada é descartado em silêncio e o envio pode ser reprocessado |
| Telemetria | API de Acompanhamento | AMQP via RabbitMQ (mensagem não persistente, com validade curta) | RF10, RNF01 | `PosicaoAtualizada` chega a cada 30 s. Perder uma é tolerável, porque a próxima corrige, e não vale pagar o custo de persistir posição |
| Pedidos, Garantia de Prazo e Faturamento | API de Acompanhamento | AMQP via RabbitMQ (persistente) | RF10 | Situação do pedido, crédito apurado e nota emitida mudam o que o cliente vê (inclusive o saldo) e não podem se perder |
| Portal do Cliente (navegador) | API de Acompanhamento | HTTP (REST, `GET`) | RF10 | Carga inicial da tela (situação, posição, previsão e saldo) em uma única resposta, lida da projeção do Acompanhamento |
| API de Acompanhamento | Portal do Cliente (navegador) | SSE (HTTP, `text/event-stream`) | RF10 | A atualização ao vivo só vai do servidor para o navegador. O SSE usa HTTP comum, reconecta sozinho e retoma do último evento com `Last-Event-ID`. WebSocket seria bidirecional sem necessidade; polling faria uma requisição a cada poucos segundos por cliente, mesmo sem novidade |

## Padrões de projeto

| Ponto da solução | Padrão | Requisito | Justificativa |
|---|---|---|---|
| Cálculo do crédito por tipo de cliente (Garantia de Prazo) | Strategy: interface `PoliticaDeCredito`, com uma política registrada para cada tipo de cliente | RF02, RF03, RF04 | A regra varia por tipo de cliente. A `CalculadoraDeCredito` só escolhe a política do tipo e delega. O tipo novo do próximo trimestre entra como uma política nova registrada, sem alterar as de Varejo, Corporativo e Cortesia (aberto para extensão, fechado para modificação). Varejo e Corporativo são a mesma estratégia por faixa de atraso, com multiplicador e teto próprios; Cortesia é a estratégia sem crédito |
| Envio pelo WhatsApp (Notificações) | Adapter (é a camada anticorrupção do mapa de contexto) | RF07 | A API do parceiro tem formato diferente do serviço de e-mail atual. Os dois ficam atrás da interface `CanalDeNotificacao.enviar(destinatario, mensagem)`: o `AdaptadorWhatsApp` traduz para o formato do parceiro e o resto do serviço não conhece esse formato. Trocar de parceiro muda só o adaptador. O canal é escolhido pela preferência do cliente |
| Retentativa de envio (Notificações) | Retry com espera crescente + Dead Letter Queue | RF08 | Depois da primeira falha, até 3 retentativas com espera crescente (por exemplo 10 s, 30 s e 90 s). Na falha da 3ª retentativa, a notificação fica como falha definitiva e vai para a fila de falhas durável, com alerta para a operação: nada é descartado em silêncio e o envio pode ser reprocessado |
| Consumo de `EntregaConfirmada` (Garantia de Prazo) | Idempotent Consumer | RF09 | O broker entrega "pelo menos uma vez" e o app reenvia quando não recebe resposta. O consumidor grava o id da confirmação e a garantia do pedido com chave única na mesma transação; a segunda entrega não tem efeito (detalhes na seção do RF09) |
| Publicação de eventos (Pedidos e Garantia de Prazo) | Transactional Outbox | RNF01, RNF02 | O fato (confirmação ou crédito) e o evento a publicar são gravados na mesma transação, e um publicador envia a outbox ao RabbitMQ. Uma queda entre gravar e publicar não perde a confirmação nem o crédito |
| Atualização ao vivo do Portal (Acompanhamento) | Observer (publish/subscribe) | RF10 | O navegador assina os eventos do pedido via SSE. Cada evento recebido gera um novo estado e a tela é redesenhada a partir dele |

### Ponto onde a dupla decidiu não aplicar padrão

**1. Decorator para o cliente Corporativo.** "Os percentuais do RF02 dobram" sugere decorar o
cálculo do Varejo e multiplicar o resultado por 2. Não aplicamos porque o decorador receberia o
valor já limitado ao teto do Varejo: com frete de R$ 1.500,00 e atraso acima de 72 h, o Varejo
devolve R$ 500,00 (R$ 750,00 limitado ao teto), o decorador dobra para R$ 1.000,00, mas o
correto é R$ 1.500,00 (100% do frete, abaixo do teto de R$ 2.000,00). Além disso, qualquer
mudança no Varejo mudaria o Corporativo sem querer, o que vai contra o RF04. A solução usa a
mesma estratégia por faixa de atraso em duas instâncias, cada uma com multiplicador e teto
próprios. O caso CT15 do plano de testes pega esse erro.

**2. Singleton para numerar as notas de crédito.** Um gerador único em memória parece garantir
a sequência, mas cada contêiner ou réplica do Faturamento teria o seu "único" gerador, e o
contador volta ao início quando o serviço reinicia: números repetidos, violando o RF06 e o
RNF03. A numeração fica no banco do Faturamento (seção abaixo).

## Confirmação de entrega duplicada (RF09)

A mesma confirmação pode chegar duas vezes por dois caminhos: o app reenvia quando não recebe
resposta, e o publicador da outbox e o RabbitMQ entregam "pelo menos uma vez". A garantia de um
único crédito fica no **consumidor de `EntregaConfirmada` da Garantia de Prazo**, apoiada nas
**chaves primárias do banco da Garantia**, e não em memória (memória não sobrevive a
reinício e não é compartilhada entre réplicas).

```sql
-- banco da Garantia de Prazo
CREATE TABLE confirmacao_processada (
    id_confirmacao UUID PRIMARY KEY,          -- id gerado no app do motorista
    pedido_id      UUID NOT NULL,
    processada_em  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE garantia_pedido (
    pedido_id      UUID PRIMARY KEY,          -- no máximo uma garantia (e um crédito) por pedido
    atraso_minutos INTEGER NOT NULL,
    valor_credito  NUMERIC(10,2) NOT NULL,
    situacao       TEXT NOT NULL              -- COM_CREDITO, SEM_CREDITO, ISENTA_POR_AUSENCIA
);

CREATE TABLE outbox (
    id        UUID PRIMARY KEY,
    tipo      TEXT NOT NULL,                  -- CreditoConcedido, AtrasoApurado
    payload   JSONB NOT NULL,
    publicado BOOLEAN NOT NULL DEFAULT false
);
```

Processamento de cada mensagem:

1. Consulta o Frete (e a Telemetria, se houve ausência) e calcula o crédito com a
   `CalculadoraDeCredito`. As chamadas HTTP ficam fora da transação.
2. Abre uma transação e insere em `confirmacao_processada`, `garantia_pedido` e `outbox`.
3. Se algum insert violar a chave primária, a confirmação já foi processada (ou o pedido já tem
   garantia apurada): desfaz a transação, confirma a mensagem (ack) e não faz mais nada.
4. Se tudo der certo, faz o commit e só então o ack. Se o serviço cair entre o commit e o ack, o
   RabbitMQ reentrega a mensagem e ela cai no passo 3.

Por que não "consultar se já existe e depois inserir": duas entregas simultâneas passariam pela
consulta ao mesmo tempo e as duas inseririam. A chave primária é verificada pelo banco de forma
atômica: com dois consumidores em paralelo, o segundo insert espera o primeiro commit e falha.

Defesas complementares: o Pedidos aceita `Idempotency-Key` no `POST` da confirmação, e o
Faturamento tem `UNIQUE (credito_id)` na nota de crédito, então um `CreditoConcedido` repetido
também não gera segunda nota. Casos de teste: CT29, CT30 e CT33.

## Numeração das notas de crédito (RF06 e RNF03)

O número sai do banco do Faturamento, na mesma transação que grava a nota:

```sql
-- banco do Faturamento
CREATE TABLE sequencia_nota_credito (
    id            SMALLINT PRIMARY KEY CHECK (id = 1),   -- uma única linha
    ultimo_numero BIGINT NOT NULL
);
INSERT INTO sequencia_nota_credito VALUES (1, 0);

CREATE TABLE nota_credito (
    numero     BIGINT PRIMARY KEY,        -- nunca repete
    credito_id UUID NOT NULL UNIQUE,      -- uma nota por crédito
    cliente_id UUID NOT NULL,
    valor      NUMERIC(10,2) NOT NULL CHECK (valor > 0),
    emitida_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- emissão, em uma única transação
BEGIN;
UPDATE sequencia_nota_credito
   SET ultimo_numero = ultimo_numero + 1
 WHERE id = 1
RETURNING ultimo_numero;                  -- trava a linha até o COMMIT
INSERT INTO nota_credito (numero, credito_id, cliente_id, valor)
VALUES (:numero, :credito_id, :cliente_id, :valor);
COMMIT;
```

- O `UPDATE` trava a linha do contador até o `COMMIT`. Emissões concorrentes esperam na fila do
  banco e cada uma lê o valor já incrementado pela anterior, então nenhum número se repete
  (RNF03).
- Se a transação falhar (por exemplo, crédito repetido barrado pelo `UNIQUE (credito_id)`), o
  incremento é desfeito junto e a sequência não fica com lacuna (RF06: sequencial).
- A chave primária em `numero` é a última barreira: mesmo com erro no código, o banco recusa
  número repetido.
- Funciona com várias réplicas do Faturamento, porque o ponto de serialização é o banco, não a
  memória do processo.
- Custo: as emissões passam uma de cada vez pelo contador, mas cada transação é curta (um
  `UPDATE` e um `INSERT`), o que basta para um crédito por pedido atrasado.
- Alternativa descartada: `SEQUENCE` do PostgreSQL. Não repete e não trava, mas não volta atrás
  quando a transação falha e deixa lacunas. Como a nota de crédito é um documento com numeração
  sequencial, preferimos o contador transacional; se lacuna fosse aceitável, a `SEQUENCE` seria
  a opção mais simples.
- Verificação: caso CT32 do plano de testes (1.000 emissões concorrentes).

## Execução em contêineres (RNF04)

Cada serviço tem seu próprio `Dockerfile` e o conjunto sobe com um único comando:
`docker compose up -d --build`. No ambiente local há um servidor PostgreSQL com um banco por
serviço (um serviço não lê o banco do outro); em produção, cada banco pode ficar em um servidor
próprio. O `depends_on` só ordena a subida: cada serviço também tenta reconectar ao broker e ao
banco quando inicia.

```yaml
services:
  rabbitmq:
    image: rabbitmq:3.13-management
    environment:
      RABBITMQ_DEFAULT_USER: logitech
      RABBITMQ_DEFAULT_PASS: logitech
    ports:
      - "5672:5672"     # AMQP
      - "15672:15672"   # painel de administração
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 10s
      retries: 5

  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: logitech
      POSTGRES_PASSWORD: logitech
    volumes:
      - ./infra/postgres:/docker-entrypoint-initdb.d   # cria um banco por serviço
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U logitech"]
      interval: 10s
      retries: 5

  telemetria:
    build: ./servicos/telemetria
    ports:
      - "9000:9000/udp"   # posições dos veículos (UDP)
      - "8080:8080"       # API HTTP (comprovação de ausência)
    environment:
      AMQP_URL: amqp://logitech:logitech@rabbitmq:5672
      DATABASE_URL: postgresql://logitech:logitech@postgres:5432/telemetria
    depends_on:
      rabbitmq: { condition: service_healthy }
      postgres: { condition: service_healthy }

  pedidos:
    build: ./servicos/pedidos              # Java
    ports: ["8081:8080"]
    environment:
      AMQP_URL: amqp://logitech:logitech@rabbitmq:5672
      DATABASE_URL: postgresql://logitech:logitech@postgres:5432/pedidos
    depends_on:
      rabbitmq: { condition: service_healthy }
      postgres: { condition: service_healthy }

  frete:
    build: ./servicos/frete                # Python
    ports: ["8082:8000"]
    environment:
      DATABASE_URL: postgresql://logitech:logitech@postgres:5432/frete
    depends_on:
      postgres: { condition: service_healthy }

  garantia-prazo:
    build: ./servicos/garantia-prazo       # Python (regra de crédito em implementacao/)
    ports: ["8083:8000"]
    environment:
      AMQP_URL: amqp://logitech:logitech@rabbitmq:5672
      DATABASE_URL: postgresql://logitech:logitech@postgres:5432/garantia
      FRETE_URL: http://frete:8000
      TELEMETRIA_URL: http://telemetria:8080
    depends_on:
      rabbitmq: { condition: service_healthy }
      postgres: { condition: service_healthy }
      frete: { condition: service_started }
      telemetria: { condition: service_started }

  faturamento:
    build: ./servicos/faturamento          # C#
    ports: ["8084:8080"]
    environment:
      AMQP_URL: amqp://logitech:logitech@rabbitmq:5672
      DATABASE_URL: postgresql://logitech:logitech@postgres:5432/faturamento
    depends_on:
      rabbitmq: { condition: service_healthy }
      postgres: { condition: service_healthy }

  notificacoes:
    build: ./servicos/notificacoes         # Node/TypeScript
    ports: ["8085:3000"]
    environment:
      AMQP_URL: amqp://logitech:logitech@rabbitmq:5672
      DATABASE_URL: postgresql://logitech:logitech@postgres:5432/notificacoes
      EMAIL_API_URL: https://email.logitech.example/api   # serviço atual
      WHATSAPP_API_URL: https://api.parceiro.example/v1   # empresa parceira
      MAX_RETENTATIVAS: "3"
    depends_on:
      rabbitmq: { condition: service_healthy }
      postgres: { condition: service_healthy }

  acompanhamento-api:
    build: ./servicos/acompanhamento-api   # Node/TypeScript, projeção de leitura e SSE
    ports: ["8086:3000"]
    environment:
      AMQP_URL: amqp://logitech:logitech@rabbitmq:5672
      DATABASE_URL: postgresql://logitech:logitech@postgres:5432/acompanhamento
    depends_on:
      rabbitmq: { condition: service_healthy }
      postgres: { condition: service_healthy }

  portal:
    build: ./servicos/portal               # React servido por nginx
    ports: ["3000:80"]
    depends_on:
      - acompanhamento-api
```
