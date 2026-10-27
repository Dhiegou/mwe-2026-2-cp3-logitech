# PRD-06 · Uso de IA e entrega final (`docs/05-uso-de-ia.md`)

> Pré-requisito: PRD-05 executado (ou interrompido por tempo depois de um passo verde).
> Siga as regras gerais do `PRDs/PRD-00-visao-geral.md`. Reserve os últimos 5 minutos para este
> PRD: commits feitos depois do encerramento não contam.

## Objetivo

Fechar o registro de uso de IA, conferir todas as entregas contra os critérios de avaliação e
fazer o último commit e push.

## Critério de avaliação que este PRD atende

> "Registro do que foi sugerido pelo assistente e do que a dupla aceitou ou descartou, com o
> motivo."

## Passos

### 1. Completar `docs/05-uso-de-ia.md`

1. Confira se a tabela tem as linhas das entregas 1 a 5 (uma por PRD). Se alguma faltar porque
   o PRD foi pulado, não invente: deixe sem a linha.
2. Acrescente, **no início da tabela** (antes da linha da entrega 1), a linha da preparação:

```markdown
| Preparação | Ao Claude (chat): ler o README do CP3 e propor como dividir o trabalho para o Claude Code | Sete PRDs na pasta PRDs/ (um por entrega) e quatro decisões para a dupla confirmar: atraso em minutos arredondados para cima (D1), RF05 no Rastreamento da Frota (D2), Cortesia avisada só acima da tolerância (D3) e Python com pytest na implementação (D4) | <resposta da dupla> | <resposta da dupla> |
```

3. Acrescente, **no fim da tabela**, a linha da execução. Na coluna "O que o assistente
   sugeriu", liste o que o próprio Claude Code propôs durante a execução que não estava nos PRDs
   (por exemplo, um ajuste de formatação ou de comando). Se não houve nada além dos PRDs,
   escreva "Nada além do conteúdo dos PRDs":

```markdown
| Execução de todas as entregas | Ao Claude Code: executar os PRDs, editar os arquivos, rodar os testes e fazer os commits | <preencher conforme a execução> | <resposta da dupla> | <resposta da dupla> |
```

4. Pergunte ao usuário a resposta da dupla para as linhas novas, como nas anteriores
   (regra 9 do PRD-00). Mostre também as linhas que ficaram com "a confirmar" e peça o motivo.
5. Logo abaixo do título `# 5. Uso de assistentes de IA`, substitua o comentário `<!-- -->` por
   este parágrafo:

```markdown
Assistentes usados: Claude (chat, no claude.ai), para analisar o enunciado e escrever os PRDs
com a proposta de cada entrega, e Claude Code, para executar os PRDs no repositório (edição dos
arquivos, execução dos testes e commits). A dupla revisou cada proposta antes de executar e
registrou abaixo o que aceitou, alterou ou descartou.
```

   Se a dupla versionou a pasta `PRDs/`, acrescente ao parágrafo: "Os PRDs usados estão na pasta
   [`PRDs/`](../PRDs/)."

### 2. Conferência final (mostre o resultado de cada item ao usuário)

- [ ] `grep -rn "<!--" README.md docs implementacao/README.md` não encontra comentários de
      instrução (a tabela `## Dupla` e o `[link do Forms]` do README não devem ser alterados
      além dos nomes e RMs).
- [ ] Nenhuma tabela de `docs/` tem linha vazia do template (`| | |`).
- [ ] Tabela `## Dupla` do `README.md` com os dois nomes e RMs.
- [ ] `cd implementacao && python -m pytest` passa. Se a saída mudou desde o passo 14 do PRD-05,
      atualize o bloco de saída no `implementacao/README.md`.
- [ ] `git log --oneline` mostra: um commit `docs:` da modelagem (feito antes de 1h10 de
      atividade), os commits das entregas 2 a 4 e os pares `test:`/`feat:` da implementação.
- [ ] O repositório é público: se o `gh` estiver disponível,
      `gh repo view --json visibility -q .visibility` deve responder `PUBLIC`. Se não estiver,
      peça ao usuário para conferir no GitHub.

### 3. Commit e push

```
git add docs/05-uso-de-ia.md implementacao/README.md
git commit -m "docs: registro do uso de IA"
git push
git status
```

`git status` deve mostrar a árvore limpa e sincronizada com `origin/main`.

### 4. Envio

Mostre ao usuário a URL do repositório (`gh repo view --json url -q .url` ou `git remote get-url
origin`) e lembre que **a dupla precisa enviar o link pelo formulário do professor** (o README
cita "[link do Forms]"). O Claude Code não envia o formulário.

## Resumo dos critérios de avaliação (para a conferência da dupla)

| Entrega | Critério do professor | Onde está atendido |
|---|---|---|
| Modelagem | Um contexto por requisito; fronteiras coerentes | `docs/01-dominio.md`: tabela de contextos, justificativa do RF05, mapa de contexto |
| Arquitetura | Protocolo justificado por requisito; padrões justificados; onde não aplicar; RF09 | `docs/02-arquitetura.md`: tabela de protocolos, tabela de padrões, Decorator e Singleton descartados, seção RF09 |
| Testes | Rastreio, limites exatos, dublês coerentes, pirâmide justificada | `docs/03-testes.md`: 39 casos, pares de limite, coluna de dublês, justificativa da proporção, mutantes |
| Tela | Tela como função do estado, estados e componentes | `docs/04-portal.md`: tipo `EstadoDaTela`, tabela de estados, árvore e props |
| Implementação | Teste antes do código no histórico; testes passando; RF02 a RF04 | `implementacao/` e `git log --oneline -- implementacao/` |
| Uso de IA | Sugestão do assistente e decisão da dupla com motivo | `docs/05-uso-de-ia.md` |
