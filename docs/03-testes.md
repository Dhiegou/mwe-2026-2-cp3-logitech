# 3. Plano de testes

## Pirâmide de testes

| Nível | Quantidade de casos | O que cobre |
|---|---|---|
| Unidade | 26 (CT01 a CT26) | Regras puras com valores-limite: faixas de atraso, tetos e arredondamento (RF02, RF03), extensão para tipo novo (RF04), apuração do atraso (RF01), comprovação de ausência (RF05) e ordem das posições recebidas por UDP (RNF01) |
| Integração | 11 (CT27 a CT37) | Fronteiras com infraestrutura e com outros serviços: isenção por ausência (RF05), eventos do cliente Cortesia (RF03), idempotência (RF09), durabilidade da fila (RNF01), numeração concorrente e nota única (RF06, RNF03), escolha do canal e adaptador (RF07), retentativas e fila de falhas (RF08) |
| Ponta a ponta | 2 (CT38 e CT39) | Fluxo completo da confirmação até a nota de crédito em até 5 min (RNF02) e tela do Portal atualizada ao vivo (RF10) |

Por que essa proporção (cerca de 67% unidade, 28% integração e 5% ponta a ponta): o maior risco
da Garantia de Prazo está em regras puras com limites exatos (faixas, tetos, multiplicador,
arredondamento e comprovação de ausência). Testes de unidade rodam em milissegundos, não
precisam de infraestrutura e permitem um caso para cada lado de cada limite. A integração fica
só para o que existe na fronteira com a infraestrutura e não pode ser verificado com regra pura:
unicidade sob concorrência e idempotência (dependem do banco real), durabilidade da fila,
formato da API do parceiro e contagem de retentativas. Ponta a ponta é lento e frágil, então
fica só para os dois requisitos medidos de fora do sistema: o prazo de 5 min (RNF02) e a tela ao
vivo (RF10).

Convenções: atraso no formato `HhMM` (ex.: `2h01`) e contado em minutos inteiros arredondados
para cima, como definido na linguagem ubíqua. Os casos CT01 a CT22 são os implementados em
TDD na pasta `implementacao/`.

## Casos de teste

| ID | Requisito | Pré-condição | Entrada | Resultado esperado | Nível | Dublê | Justificativa do dublê |
|---|---|---|---|---|---|---|---|
| CT01 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 1h59 | Crédito de R$ 0,00 | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT02 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 2h00 (limite da tolerância) | Crédito de R$ 0,00 | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT03 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 2h01 | Crédito de R$ 30,00 (10%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT04 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 24h00 | Crédito de R$ 30,00 (10%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT05 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 24h01 | Crédito de R$ 75,00 (25%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT06 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 72h00 | Crédito de R$ 75,00 (25%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT07 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 72h01 | Crédito de R$ 150,00 (50%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT08 | RF02 | Cliente Varejo, frete de R$ 1.000,00 | Atraso de 72h01 | Crédito de R$ 500,00 (50% igual ao teto) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT09 | RF02 | Cliente Varejo, frete de R$ 1.000,02 | Atraso de 72h01 | Crédito de R$ 500,00 (50% daria R$ 500,01, um centavo acima do teto) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT10 | RF02 | Cliente Varejo, frete de R$ 123,45 | Atraso de 2h01 | Crédito de R$ 12,35 (10% = R$ 12,345, arredondado ao centavo, meio para cima) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT11 | RF03 | Cliente Corporativo, frete de R$ 300,00 | Atraso de 2h00 | Crédito de R$ 0,00 (a tolerância não muda) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT12 | RF03 | Cliente Corporativo, frete de R$ 300,00 | Atraso de 2h01 | Crédito de R$ 60,00 (20%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT13 | RF03 | Cliente Corporativo, frete de R$ 300,00 | Atraso de 24h01 | Crédito de R$ 150,00 (50%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT14 | RF03 | Cliente Corporativo, frete de R$ 300,00 | Atraso de 72h01 | Crédito de R$ 300,00 (100%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT15 | RF03 | Cliente Corporativo, frete de R$ 1.500,00 | Atraso de 72h01 | Crédito de R$ 1.500,00 (acima do teto do Varejo e abaixo do teto do Corporativo) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT16 | RF03 | Cliente Corporativo, frete de R$ 2.000,00 | Atraso de 72h01 | Crédito de R$ 2.000,00 (100% igual ao teto) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT17 | RF03 | Cliente Corporativo, frete de R$ 2.000,01 | Atraso de 72h01 | Crédito de R$ 2.000,00 (100% daria R$ 2.000,01, um centavo acima do teto) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT18 | RF03 | Cliente Cortesia, frete de R$ 0,00 | Atraso de 72h01 | Crédito de R$ 0,00 (o aviso ao cliente é verificado no CT28) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT19 | RF04 | Calculadora padrão mais o tipo novo "PREMIUM", registrado com uma política que devolve R$ 42,00 | PREMIUM com atraso de 5h00; Varejo e Corporativo com frete de R$ 300,00 e atraso de 2h01 | PREMIUM: R$ 42,00; Varejo: R$ 30,00; Corporativo: R$ 60,00 (iguais aos de CT03 e CT12) | Unidade | Stub | O caso verifica só que a calculadora usa a política registrada para o tipo novo sem mudar as existentes. Um stub de valor fixo dá essa resposta sem depender de uma regra que ainda não existe |
| CT20 | RF04 | Calculadora padrão | Tipo "ATACADO" (não registrado), frete de R$ 300,00, atraso de 5h00 | Erro `TipoDeClienteNaoSuportado`, nunca um crédito zero silencioso | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT21 | RF01 | Prazo prometido em 10/11/2026 14:00 | Confirmação em 10/11/2026 13:30 | Atraso de 0 min (entrega antecipada não gera atraso negativo) | Unidade | Nenhum | Cálculo puro sobre dois horários |
| CT22 | RF01 | Prazo prometido em 10/11/2026 14:00 | Confirmação em 10/11/2026 16:00:30 | Atraso de 121 min (minuto iniciado conta), acima da tolerância | Unidade | Nenhum | Cálculo puro sobre dois horários |
| CT23 | RF05 | Posições do veículo a 200 m do endereço, velocidade zero, a cada 30 s, de 14:00:00 a 14:10:00 | Ausência registrada às 14:10:00 | Ausência comprovada | Unidade | Nenhum | O verificador recebe as posições como parâmetro: é uma função pura |
| CT24 | RF05 | Igual ao CT23, mas com o veículo a 201 m do endereço | Ausência registrada às 14:10:00 | Ausência não comprovada | Unidade | Nenhum | Função pura, sem dependência externa |
| CT25 | RF05 | Posições a 50 m do endereço, velocidade zero, de 14:00:30 a 14:10:00 (9 min 30 s) | Ausência registrada às 14:10:00 | Ausência não comprovada | Unidade | Nenhum | Função pura, sem dependência externa |
| CT26 | RNF01 | Veículo com posição atual medida às 14:01:00 | Chega um pacote com posição medida às 14:00:30 (fora de ordem) | A posição atual continua a das 14:01:00 | Unidade | Nenhum | Regra do agregado `Veiculo`, sem rede |
| CT27 | RF05 | Garantia de Prazo; pedido Varejo, frete de R$ 300,00, atraso de 30h00, com ausência registrada | A Telemetria responde "ausência comprovada" | Garantia isenta, crédito de R$ 0,00 e nenhum `CreditoConcedido` gravado na outbox | Integração | Stub | Só é preciso controlar a resposta da Telemetria (entrada indireta). O que se verifica é o estado final da garantia, não a chamada |
| CT28 | RF03 | Garantia de Prazo; cliente Cortesia, frete de R$ 0,00 | `EntregaConfirmada` com atraso de 5h00 | Publica `AtrasoApurado` com crédito de R$ 0,00 e não publica `CreditoConcedido` | Integração | Spy | O que se verifica são as saídas indiretas (eventos publicados). O spy registra cada publicação para conferir depois |
| CT29 | RF09 | Garantia com PostgreSQL e RabbitMQ reais em contêiner; pedido Varejo, frete de R$ 300,00, atraso de 30h00 | A mesma `EntregaConfirmada` (id C-1) entregue duas vezes, uma depois da outra | Um crédito de R$ 75,00 e um `CreditoConcedido` na outbox; a 2ª mensagem recebe ack sem efeito | Integração | Nenhum | A garantia está na chave primária do banco; um dublê do banco esconderia justamente o que se quer testar |
| CT30 | RF09 | Igual ao CT29, com dois consumidores ativos | A mesma confirmação entregue aos dois consumidores ao mesmo tempo | Um único crédito | Integração | Nenhum | A condição de corrida só aparece com banco e concorrência reais |
| CT31 | RNF01 | Garantia de Prazo parada; RabbitMQ real | O Pedidos publica `EntregaConfirmada` e a Garantia sobe 1 min depois | A mensagem continua na fila durável e gera o crédito quando a Garantia sobe | Integração | Nenhum | A durabilidade da fila é o próprio objeto do teste |
| CT32 | RF06, RNF03 | Faturamento com PostgreSQL real, contador zerado | 1.000 `CreditoConcedido` diferentes processados em paralelo (50 threads) | 1.000 notas com números de 1 a 1.000, sem repetição e sem lacuna | Integração | Nenhum | A concorrência real no banco é o que se verifica |
| CT33 | RF06 | Faturamento com PostgreSQL real | O mesmo `CreditoConcedido` (id K-1) entregue duas vezes | Uma única nota de crédito | Integração | Nenhum | A restrição única do banco é o que se verifica |
| CT34 | RF07 | Cliente com canal preferido WhatsApp | `AtrasoApurado` do pedido | O adaptador chama a API do parceiro uma vez, com o corpo no formato do parceiro; o serviço de e-mail não é chamado | Integração | Mock | O caso verifica a interação: qual canal é chamado e com que formato. O mock tem a chamada esperada e falha se ela não acontecer ou vier diferente |
| CT35 | RF07 | Cliente com canal preferido e-mail | `AtrasoApurado` do pedido | O serviço de e-mail atual é chamado uma vez; a API do parceiro não é chamada | Integração | Mock | Mesmo motivo do CT34: o resultado é a interação com o canal certo |
| CT36 | RF08 | Canal que falha nas 3 primeiras tentativas e responde OK na 4ª | `AtrasoApurado` do pedido | Notificação enviada na 4ª tentativa (3ª retentativa); fila de falhas vazia | Integração | Spy | O spy simula as falhas e conta as chamadas: o resultado depende do número exato de tentativas |
| CT37 | RF08 | Canal que falha sempre | `AtrasoApurado` do pedido | Exatamente 4 tentativas (1 + 3 retentativas), nenhuma 5ª; notificação na fila de falhas com o motivo e alerta registrado | Integração | Spy | Mesmo motivo do CT36: é preciso contar as tentativas |
| CT38 | RNF02, RF06 | Ambiente completo no ar (`docker compose up`); pedido Varejo, frete de R$ 300,00 | O app confirma a entrega 30h00 depois do prazo prometido | Nota de crédito de R$ 75,00 emitida em até 5 min após a confirmação | Ponta a ponta | Nenhum | Mede o tempo real do fluxo entre todos os serviços |
| CT39 | RF10 | Ambiente completo no ar; Portal aberto em um pedido Varejo em trânsito, frete de R$ 300,00 | O simulador do veículo envia nova posição por UDP; depois, o app confirma a entrega com atraso de 3h00 | Mapa e previsão mudam sem recarregar a página; depois da nota emitida, o saldo de créditos aumenta R$ 30,00 | Ponta a ponta | Nenhum | Verifica o caminho real até o navegador (AMQP, SSE e React) |

## Mutante que o plano detecta

| Mutante | Caso que o detecta | Por quê |
|---|---|---|
| Na tolerância, trocar `atraso > 120 min` por `atraso >= 120 min` | CT02 | Com atraso de 2h00 o mutante paga R$ 30,00; o caso espera R$ 0,00 |
| Na segunda faixa, trocar `atraso > 1.440 min` por `atraso >= 1.440 min` | CT04 | Com 24h00 o mutante paga 25% (R$ 75,00); o caso espera R$ 30,00 |
| Remover a limitação ao teto (`min(credito, teto)`) | CT09 | O mutante devolve R$ 500,01; o caso espera R$ 500,00 |
| Calcular o Corporativo como "resultado do Varejo × 2" (Decorator) | CT15 | O teto de R$ 500,00 do Varejo é aplicado antes de dobrar: o mutante devolve R$ 1.000,00 e o caso espera R$ 1.500,00 |
| Trocar o arredondamento "meio para cima" por truncamento | CT10 | O mutante devolve R$ 12,34; o caso espera R$ 12,35 |
| Na retentativa, parar em `tentativa < 3` em vez de `tentativa <= 3` | CT36 | O mutante desiste depois da 2ª retentativa e manda para a fila de falhas uma notificação que seria entregue na 3ª |
