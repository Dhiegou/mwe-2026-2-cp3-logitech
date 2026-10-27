# PRD-00 · Visão geral e regras de execução (CP3 Garantia de Prazo LogiTech)

> Leia este arquivo inteiro antes de executar qualquer outro PRD desta pasta.
> Todos os PRDs foram escritos para o Claude Code executar dentro do repositório da dupla
> (criado a partir do template `josercf/mwe-2026-2-cp3-logitech`).

## 1. Objetivo

Preencher as entregas do CP3 descritas no `README.md` do repositório:

| PRD | Entrega | Arquivo alterado | Tempo sugerido no README |
|---|---|---|---|
| PRD-01 | 1. Modelagem do domínio | `docs/01-dominio.md` | 0:10 a 0:40 (commit obrigatório até 1:10) |
| PRD-02 | 2. Arquitetura | `docs/02-arquitetura.md` | 0:40 a 1:10 |
| PRD-03 | 3. Plano de testes | `docs/03-testes.md` | 1:10 a 1:50 |
| PRD-04 | 4. Tela do Portal do Cliente | `docs/04-portal.md` | 1:50 a 2:00 |
| PRD-05 | 5. Implementação em TDD | `implementacao/` | 2:00 a 2:25 |
| PRD-06 | Uso de IA e entrega final | `docs/05-uso-de-ia.md`, `implementacao/README.md` | 2:25 a 2:30 |

Execute na ordem. Cada PRD termina com commit e push. Não pule o push: o professor avalia o
repositório no GitHub e só considera commits feitos antes do encerramento.

## 2. Preparação (fazer uma vez, antes do PRD-01)

1. A dupla cria o repositório com **Use this template** no GitHub e o deixa **público**.
   Alternativa pelo terminal, se o `gh` estiver autenticado:
   `gh repo create <usuario>/<nome-do-repo> --template josercf/mwe-2026-2-cp3-logitech --public --clone`
2. Abra o repositório clonado (ou o Codespace dele) e coloque esta pasta `PRDs/` na raiz.
3. Peça ao usuário o **nome e o RM** dos dois integrantes e preencha a tabela `## Dupla` do
   `README.md`. Não altere mais nada no `README.md`.
4. Confirme com `git remote -v` que o `origin` aponta para o repositório da dupla (e não para o
   template do professor). Se apontar para o template, pare e avise o usuário.
5. Pergunte ao usuário se a dupla quer versionar a pasta `PRDs/`. Recomendação: sim, porque
   documenta o uso de IA exigido no `docs/05-uso-de-ia.md`. Se sim, ela entra no commit do PRD-01.

## 3. Decisões que a dupla deve confirmar antes do PRD-01

Os PRDs já trazem uma proposta para cada uma. Mostre a lista ao usuário e pergunte se a dupla
aceita todas. Se alguma mudar, ajuste os PRDs afetados antes de executá-los e registre a mudança
no `docs/05-uso-de-ia.md`.

| # | Decisão proposta | PRDs afetados |
|---|---|---|
| D1 | O atraso é contado em **minutos inteiros arredondados para cima** (um minuto iniciado conta). Como os limites das faixas são minutos exatos (120, 1.440 e 4.320), isso classifica igual a comparar os horários exatos | 01, 03, 05 |
| D2 | O RF05 (comprovação de ausência) fica no contexto **Rastreamento da Frota**, porque a regra fala de posição, distância e tempo parado. A Garantia só consome o resultado | 01, 02 |
| D3 | O cliente Cortesia é avisado quando o atraso **passa da tolerância de 2 h**, igual ao ponto em que os outros tipos ganham crédito | 01, 02, 03 |
| D4 | Implementação em **Python 3 com pytest** (menos configuração para caber nos 25 minutos) | 05, 06 |

## 4. Regras gerais para o Claude Code

1. Escreva tudo em português do Brasil, com acentuação correta.
2. Não use travessão (—) como conector no texto. Use vírgula, dois-pontos ou parênteses.
3. Altere somente os arquivos listados no PRD em execução. Não crie serviços, `compose.yaml`
   real, nem código fora de `implementacao/`: o compose da entrega 2 é só um esboço dentro do
   documento.
4. Mantenha a estrutura de cada arquivo de `docs/` (títulos e colunas das tabelas). Preencha
   com o conteúdo do PRD e apague os comentários `<!-- -->` depois de atendê-los, como pede o
   README.
5. O conteúdo técnico dos PRDs (requisitos, valores, nomes de contextos, IDs de casos de teste)
   deve ser copiado sem alteração. Pode ajustar quebra de linha e formatação Markdown.
6. Diagramas Mermaid: mantenha os rótulos entre aspas, como estão nos PRDs. Se houver
   `npx`/`mmdc` disponível, valide a sintaxe; se não, apenas confira se o bloco começa com
   ` ```mermaid ` e fecha com ` ``` `.
7. Commits: Conventional Commits, mensagem em português, no formato que o PRD indicar.
   Faça push depois de cada commit de entrega.
8. Nunca reescreva o histórico (`--amend`, `rebase`, `push --force`): o histórico é a evidência
   do TDD e do commit até 1h10.
9. Registro de uso de IA: cada PRD traz a linha que deve entrar em `docs/05-uso-de-ia.md`.
   Antes do commit, mostre a linha ao usuário e pergunte se a dupla aceita a proposta como está
   ou se alterou/descartou algo. Preencha as colunas "Decisão da dupla" e "Motivo" com a resposta
   do usuário, nunca por conta própria. Se o usuário pedir para seguir sem responder, escreva
   "a confirmar" nas duas colunas e avise no resumo final (o PRD-06 cobra essas linhas).
10. Ao terminar cada PRD, mostre um resumo curto: arquivos alterados, hash do commit e se o push
    foi feito.

## 5. Como acionar no Claude Code

```
Leia PRDs/PRD-00-visao-geral.md e depois execute PRDs/PRD-01-modelagem-dominio.md.
```

Depois, um PRD por vez: `Execute PRDs/PRD-02-arquitetura.md`, e assim por diante.

## 6. Visão da solução (resumo para dar contexto a todos os PRDs)

- Contexto novo **Garantia de Prazo** (serviço Python) apura o atraso e calcula o crédito com
  uma **política de crédito por tipo de cliente** (Strategy). Varejo: faixas 0%/10%/25%/50% e
  teto de R$ 500. Corporativo: percentuais dobrados e teto de R$ 2.000. Cortesia: sem crédito,
  mas recebe aviso.
- **Telemetria** recebe posições por UDP (perda tolerada). A confirmação de entrega chega ao
  **Pedidos** por HTTPS com chave de idempotência e segue para a Garantia por **AMQP**
  (RabbitMQ, fila durável). A Garantia consulta **Frete** e **Telemetria** por HTTP.
- RF09: **consumidor idempotente** com restrição única no banco da Garantia.
- RF06/RNF03: número da nota gerado por **contador transacional no banco do Faturamento**.
- RF07/RF08: **Adapter** para o WhatsApp do parceiro, retentativas e **fila de falhas**.
- RF10: Portal em React recebe atualizações por **SSE** e a tela é uma função do estado.
- Implementação: núcleo da regra de crédito em Python, com TDD (teste antes do código em
  commits separados).
