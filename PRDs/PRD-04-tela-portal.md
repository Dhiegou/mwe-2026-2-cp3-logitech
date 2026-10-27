# PRD-04 · Tela do Portal do Cliente (`docs/04-portal.md`)

> Pré-requisito: PRD-03 executado. Siga as regras gerais do `PRDs/PRD-00-visao-geral.md`.

## Objetivo

Preencher `docs/04-portal.md` descrevendo a tela de acompanhamento do pedido como função do
estado: os estados possíveis, os dados de cada um, os componentes que os exibem e de onde vêm os
dados, incluindo a atualização ao vivo (RF10).

## Critério de avaliação que este PRD atende

> "Tela descrita como função do estado, com os estados possíveis e os componentes que os
> exibem."

## Escopo

- Alterar: `docs/04-portal.md` e `docs/05-uso-de-ia.md` (uma linha).
- Não criar código React no repositório: os trechos de código ficam só dentro do documento.

## Passos

1. Substitua todo o conteúdo de `docs/04-portal.md` pelo conteúdo da seção "Conteúdo final".
2. Confira os critérios de aceite.
3. Acrescente a linha de uso de IA em `docs/05-uso-de-ia.md`.
4. Commit e push.

## Conteúdo final de `docs/04-portal.md`

````markdown
# 4. Tela do Portal do Cliente (RF10)

A tela de acompanhamento é uma função do estado: `tela = f(estado)`. O componente raiz não
guarda indicadores soltos (`carregando`, `temErro`, `atrasado`...) que poderiam se contradizer.
Ele guarda um único estado, de um tipo que só admite combinações válidas, e cada estado decide
quais componentes aparecem. Tudo que chega do servidor (carga inicial e eventos SSE) passa por
um reducer que devolve o próximo estado.

```ts
type Conexao = 'aoVivo' | 'reconectando';

type MotivoSemCredito = 'noPrazo' | 'dentroDaTolerancia' | 'cortesia' | 'ausenciaComprovada';

type SituacaoDoCredito =
  | { tipo: 'processando' }
  | { tipo: 'concedido'; valor: number; numeroNota: number }
  | { tipo: 'semCredito'; motivo: MotivoSemCredito };

// ResumoDoPedido: número, destino (com coordenadas) e prazo prometido.
// Posicao: latitude, longitude e horário da medição.
type EstadoDaTela =
  | { tipo: 'carregando' }
  | { tipo: 'erro'; mensagem: string }
  | { tipo: 'aguardandoSaida'; pedido: ResumoDoPedido; saldo: number }
  | { tipo: 'emTransito'; pedido: ResumoDoPedido; posicao: Posicao; previsaoChegada: string; conexao: Conexao; saldo: number }
  | { tipo: 'ausenciaRegistrada'; pedido: ResumoDoPedido; registradaEm: string; saldo: number }
  | { tipo: 'entregue'; pedido: ResumoDoPedido; entregueEm: string; atrasoMinutos: number; credito: SituacaoDoCredito; saldo: number };

function AcompanhamentoPedido({ pedidoId }: { pedidoId: string }) {
  const [estado, despachar] = useReducer(reducerDoAcompanhamento, { tipo: 'carregando' });
  useAcompanhamentoAoVivo(pedidoId, despachar); // carga inicial + EventSource

  switch (estado.tipo) {
    case 'carregando':
      return <EsqueletoAcompanhamento />;
    case 'erro':
      return <MensagemDeErro mensagem={estado.mensagem} onTentarNovamente={() => despachar({ tipo: 'recarregar' })} />;
    default:
      return <PainelDoPedido estado={estado} />;
  }
}
```

## Estados da tela

| Estado | Dados disponíveis | O que a tela exibe |
|---|---|---|
| `carregando` | Só o id do pedido, que vem da URL | `EsqueletoAcompanhamento`: blocos cinza no lugar do mapa e dos cartões |
| `erro` | Mensagem da falha na carga inicial | `MensagemDeErro` com o texto e o botão "Tentar novamente" |
| `aguardandoSaida` | Pedido (número, destino e prazo prometido) e saldo; ainda sem posição do veículo | `CabecalhoDoPedido` com "Aguardando saída", `MapaDoVeiculo` só com o destino, `PrevisaoDeChegada` mostrando o prazo prometido e `SaldoDeCreditos` |
| `emTransito` com conexão ao vivo | Pedido, posição (latitude, longitude e horário da medição), previsão de chegada e saldo | `CabecalhoDoPedido` com "Em trânsito", `IndicadorAoVivo` ("Ao vivo · atualizado há 12 s"), `MapaDoVeiculo` com o veículo e o destino, `PrevisaoDeChegada` e `SaldoDeCreditos` |
| `emTransito` com previsão depois do prazo (derivado: previsão de chegada maior que o prazo prometido) | Os mesmos do estado anterior | Tudo do estado anterior, mais `AvisoDeAtraso`: "A previsão de chegada passou do prazo prometido (14:00)". O aviso não promete crédito, porque o crédito depende do atraso real e do tipo de cliente |
| `emTransito` reconectando | Última posição e última previsão recebidas, com o horário | `IndicadorAoVivo` em "Reconectando…", `MapaDoVeiculo` com o veículo esmaecido e "Última posição às 14:02"; o restante igual ao estado ao vivo |
| `ausenciaRegistrada` | Pedido, horário do registro de ausência e saldo | `CabecalhoDoPedido` com "Destinatário ausente", `AvisoDeAusencia` com o horário do registro e a orientação para reagendar, e `SaldoDeCreditos` |
| `entregue` com crédito em processamento | Horário da entrega, atraso e saldo ainda sem o crédito | `ResumoDaEntrega` ("Entregue às 17:01, 3h01 depois do prazo"), `CreditoDoPedido` com "Crédito em processamento (até 5 min)" e `SaldoDeCreditos` |
| `entregue` com crédito concedido | Horário da entrega, atraso, valor do crédito, número da nota e saldo atualizado | `ResumoDaEntrega`, `CreditoDoPedido` ("Crédito de R$ 30,00 · nota nº 1.234") e `SaldoDeCreditos` com o novo saldo em destaque |
| `entregue` sem crédito | Horário da entrega, atraso e motivo: no prazo, dentro da tolerância, cliente Cortesia ou ausência comprovada | `ResumoDaEntrega` e `CreditoDoPedido` com o motivo ("Entregue no prazo", "Atraso dentro da tolerância de 2 h", "Seu contrato não prevê crédito" ou "Ausência do destinatário comprovada"), mais `SaldoDeCreditos` |

## Árvore de componentes

```
<AcompanhamentoPedido pedidoId>
  <EsqueletoAcompanhamento />
  <MensagemDeErro mensagem onTentarNovamente />
  <PainelDoPedido estado>
    <CabecalhoDoPedido numero situacao prazoPrometido />
    <IndicadorAoVivo conexao atualizadoEm />
    <MapaDoVeiculo destino posicao desatualizada />
    <PrevisaoDeChegada previsaoChegada prazoPrometido>
      <AvisoDeAtraso previsaoChegada prazoPrometido />
    </PrevisaoDeChegada>
    <AvisoDeAusencia registradaEm />
    <ResumoDaEntrega entregueEm atrasoMinutos />
    <CreditoDoPedido credito />
    <SaldoDeCreditos saldo destacar />
  </PainelDoPedido>
</AcompanhamentoPedido>
```

| Componente | Props recebidas | Responsabilidade |
|---|---|---|
| `AcompanhamentoPedido` | `pedidoId` | Único componente com estado. Faz a carga inicial, abre o `EventSource`, passa cada evento pelo reducer e escolhe entre esqueleto, erro e painel |
| `EsqueletoAcompanhamento` | Nenhuma | Mostra a forma da tela enquanto a carga inicial não volta |
| `MensagemDeErro` | `mensagem`, `onTentarNovamente` | Explica a falha e permite repetir a carga inicial |
| `PainelDoPedido` | `estado` (qualquer estado, exceto `carregando` e `erro`) | Decide quais filhos aparecem conforme `estado.tipo`. Não tem estado próprio |
| `CabecalhoDoPedido` | `numero`, `situacao`, `prazoPrometido` | Mostra o número do pedido, a situação em texto e o prazo prometido |
| `IndicadorAoVivo` | `conexao` (`aoVivo` ou `reconectando`), `atualizadoEm` | Mostra "Ao vivo · atualizado há X s" ou "Reconectando…". Aparece só em `emTransito` |
| `MapaDoVeiculo` | `destino`, `posicao` (opcional), `desatualizada` | Desenha o destino e, quando houver, o veículo. Esmaece o veículo quando a conexão cai |
| `PrevisaoDeChegada` | `previsaoChegada` (opcional), `prazoPrometido` | Mostra a previsão (ou só o prazo, antes da saída) e decide se exibe o aviso de atraso |
| `AvisoDeAtraso` | `previsaoChegada`, `prazoPrometido` | Avisa que a previsão passou do prazo prometido. Aparece só quando a previsão é maior que o prazo |
| `AvisoDeAusencia` | `registradaEm` | Informa a tentativa sem destinatário e como reagendar. Aparece só em `ausenciaRegistrada` |
| `ResumoDaEntrega` | `entregueEm`, `atrasoMinutos` | Mostra quando o pedido foi entregue e o atraso em horas e minutos. Aparece só em `entregue` |
| `CreditoDoPedido` | `credito` (`SituacaoDoCredito`) | Mostra "em processamento", o valor com o número da nota, ou o motivo de não haver crédito. Aparece só em `entregue` |
| `SaldoDeCreditos` | `saldo`, `destacar` | Mostra o saldo de créditos e o destaca por alguns segundos quando ele muda |

## Origem dos dados

| Dado | Contexto de origem | Como chega à tela |
|---|---|---|
| Número, destino e prazo prometido | Pedidos (prazo calculado pelo Frete) | Carga inicial: `GET /api/acompanhamento/pedidos/{id}` na API de Acompanhamento, que responde a partir da sua projeção de leitura |
| Posição do veículo e previsão de chegada | Rastreamento da Frota (Telemetria) | Evento `PosicaoAtualizada` (AMQP, a cada 30 s) → API de Acompanhamento → evento SSE `posicao` |
| Ausência registrada e entrega confirmada | Pedidos | Eventos `AusenciaRegistrada` e `EntregaConfirmada` (AMQP) → eventos SSE `ausencia` e `entrega` |
| Crédito apurado ou motivo de não haver crédito | Garantia de Prazo | Evento `AtrasoApurado` (AMQP) → evento SSE `credito` |
| Número da nota e saldo de créditos | Faturamento | Saldo na carga inicial; depois, evento `NotaDeCreditoEmitida` (AMQP) → eventos SSE `credito` e `saldo` |

Como a atualização ao vivo chega ao navegador:

1. Ao montar, `AcompanhamentoPedido` faz a carga inicial e despacha `carregou` (ou `falhou`)
   para o reducer.
2. Em seguida abre `new EventSource('/api/acompanhamento/pedidos/{id}/eventos')`. Cada evento
   SSE (`posicao`, `ausencia`, `entrega`, `credito`, `saldo`) vira uma ação do reducer, que
   devolve o próximo estado, e o React redesenha só o que mudou.
3. Se a conexão cai, o `onerror` do `EventSource` despacha `conexaoPerdida` e o indicador vai
   para "Reconectando…". O navegador reconecta sozinho enviando o `Last-Event-ID`; a API reenvia
   os eventos perdidos ou um evento `snapshot` com o estado atual, e o indicador volta a "Ao vivo".
4. Como a posição vem de UDP, um pacote perdido só significa que a próxima posição chega 30 s
   depois: a tela mostra "atualizado há X s" em vez de travar.
5. A tela não calcula atraso nem crédito. Ela só exibe o que a Garantia de Prazo e o Faturamento
   informam, para não duplicar regra de negócio no front-end.
````

## Critérios de aceite

- [ ] Nenhum comentário `<!-- -->` sobrou em `docs/04-portal.md`.
- [ ] Todo componente citado na tabela de estados existe na árvore e na tabela de componentes.
- [ ] Os blocos ` ```ts ` e o bloco da árvore abrem e fecham corretamente (confira o preview).
- [ ] Nenhum travessão (—) no arquivo.

## Registro de uso de IA (`docs/05-uso-de-ia.md`)

Acrescente esta linha ao fim da tabela, com as duas últimas colunas preenchidas pela dupla:

```markdown
| 4. Tela do Portal | Ao Claude (chat): descrever a tela de acompanhamento como função do estado, em forma de PRD | Estado único com tipo discriminado (carregando, erro, aguardando saída, em trânsito ao vivo ou reconectando, ausência registrada, entregue com crédito em processamento, concedido ou sem crédito); reducer alimentado pela carga inicial e por SSE; 13 componentes com props; a tela não calcula crédito | <resposta da dupla> | <resposta da dupla> |
```

## Commit

```
git add docs/04-portal.md docs/05-uso-de-ia.md
git commit -m "docs: tela de acompanhamento do Portal do Cliente"
git push
```
