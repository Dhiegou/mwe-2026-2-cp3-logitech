# PRD-07 · Ajustes da revisão final

> Pré-requisito: PRD-06 executado. Siga as regras gerais do `PRDs/PRD-00-visao-geral.md`.
> Este PRD não altera `docs/01` a `docs/04`, nem o código e os testes de `implementacao/`: o
> histórico de TDD precisa ficar exatamente como está. Em `implementacao/`, só o `README.md` muda.

## Objetivo

Fechar os pontos levantados na revisão do repositório entregue:

1. Explicar a autoria dos commits, que aparecem como "Laboratório FIAP" (configuração padrão do
   git do computador do laboratório), e fazer os commits novos com o nome da dupla.
2. Conferir se `README.md` e `.devcontainer/devcontainer.json` estão mesmo modificados na cópia
   local (na revisão, a diferença parecia ser só de fim de linha).
3. Tornar a evidência do TDD verificável: tabela com o resultado dos testes em cada commit.
4. Registrar a revisão no `docs/05-uso-de-ia.md`, inclusive o que a dupla descartou.

## Fora do escopo (não fazer)

- Recriar o repositório com "Use this template": o professor autorizou o fork em aula. Isso
  entra no `docs/05` como sugestão descartada (passo 5).
- Reescrever o histórico (`rebase`, `filter-branch`, `--amend`, `push --force`) para trocar
  autor ou datas: mudaria o hash de todos os commits, inclusive os pares de TDD.
- Horário do commit da modelagem: não há ação possível.

## Passos

### 1. Conferir a cópia local

```
git fetch
git status
```

- A branch deve estar sincronizada com `origin/main`. Se estiver atrás, rode `git pull --ff-only`.
- Se `README.md` ou `.devcontainer/devcontainer.json` aparecerem como modificados, rode
  `git diff --ignore-cr-at-eol --stat -- README.md .devcontainer/devcontainer.json`:
  - se não mostrar nenhuma diferença, é só fim de linha: descarte com
    `git checkout -- README.md .devcontainer/devcontainer.json`;
  - se mostrar diferença de conteúdo, pare e mostre o diff ao usuário antes de seguir.
- Anote qual dos casos aconteceu (arquivos não modificados, ou modificados só no fim de linha):
  ele define a linha 3 do passo 5.

### 2. Identidade do git para os commits novos

Pergunte ao usuário:

- nome e e-mail de quem vai aparecer como autor (sugestão: Dhiego Ferreira de Queiroz);
- e-mail do outro integrante para a linha `Co-authored-by` (Thiago Cardoso Mendes Machado).

Para o GitHub ligar o commit à conta, o e-mail precisa ser um dos e-mails da conta. Como o
repositório é público, sugira o e-mail "noreply" do GitHub (Settings, Emails), que não expõe o
e-mail pessoal. Se o usuário não souber o e-mail do colega, faça os commits sem a linha
`Co-authored-by`.

Configure só neste repositório, **sem** `--global` (o computador do laboratório é compartilhado):

```
git config user.name "<nome informado>"
git config user.email "<e-mail informado>"
```

### 3. Observação de autoria no `README.md`

Logo abaixo da tabela `## Dupla` (depois da linha do segundo integrante), deixe uma linha em
branco e acrescente:

```markdown
> Autoria dos commits: os commits feitos no computador do laboratório aparecem com o autor
> "Laboratório FIAP", que é a configuração padrão do git dessa máquina. A dupla autora é a da
> tabela acima. Os commits seguintes usam o nome da dupla.
```

Se o passo 2 não configurou a identidade, apague a última frase. Não altere mais nada no README.

### 4. Evidência do TDD em `implementacao/README.md`

Salve o script abaixo **fora do repositório** (por exemplo, na pasta temporária do sistema) e
rode-o a partir da raiz do repositório: `python <caminho>/evidencia_tdd.py`. Ele extrai cada
commit com `git archive` para uma pasta temporária e roda o pytest lá; não mexe na pasta de
trabalho nem no histórico. Leva menos de um minuto.

```python
"""Roda os testes no código de cada commit de implementacao/ e imprime a tabela de evidência do TDD.

Uso, na raiz do repositório: python <caminho>/evidencia_tdd.py
Não altera o repositório nem a pasta de trabalho: cada commit é extraído com `git archive`
para uma pasta temporária, onde o pytest roda.
"""
import io
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

TRADUCAO = {"passed": ("passou", "passaram"), "failed": ("falhou", "falharam"),
            "error": ("erro", "erros"), "errors": ("erro", "erros")}


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def resultado_dos_testes(sha: str) -> str:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as pasta:
        conteudo = io.BytesIO(git("archive", "--format=tar", sha, "implementacao"))
        with tarfile.open(fileobj=conteudo, mode="r:") as tar:
            if hasattr(tarfile, "data_filter"):
                tar.extractall(pasta, filter="data")
            else:
                tar.extractall(pasta)
        impl = Path(pasta) / "implementacao"
        if not (impl / "tests").is_dir():
            return "Sem testes"
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        saida = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                               cwd=impl, env=env, capture_output=True, text=True,
                               encoding="utf-8", errors="replace").stdout
    linhas = saida.strip().splitlines()
    resumo = linhas[-1] if linhas else ""
    partes = []
    for qtd, tipo in re.findall(r"(\d+) (passed|failed|errors?)\b", resumo):
        singular, plural = TRADUCAO[tipo]
        partes.append(f"{qtd} {singular if qtd == '1' else plural}")
    return ", ".join(partes) or resumo


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    log = git("log", "--reverse", "--format=%h%x09%s", "--", "implementacao/").decode("utf-8")
    commits = [linha.split("\t", 1) for linha in log.splitlines()]
    print("| Passo | Commit de teste | Resultado no commit de teste | Commit de código | Resultado no commit de código |")
    print("|---|---|---|---|---|")
    i = 0
    while i < len(commits):
        sha, msg = commits[i]
        if msg.startswith("test:") and i + 1 < len(commits) and commits[i + 1][1].startswith("feat:"):
            palavras = re.sub(r"^test:\s*", "", msg).split(" ")[:3]
            passo = " ".join(p for p in palavras if p.startswith("CT") or p in ("e", "a"))
            feat_sha, feat_msg = commits[i + 1]
            print(f"| {passo} | `{sha}` {msg} | {resultado_dos_testes(sha)} "
                  f"| `{feat_sha}` {feat_msg} | {resultado_dos_testes(feat_sha)} |")
            i += 2
        elif msg.startswith("refactor:"):
            print(f"| Refatoração | Sem teste novo | Sem teste novo | `{sha}` {msg} | {resultado_dos_testes(sha)} |")
            i += 1
        else:
            i += 1


if __name__ == "__main__":
    main()
```

Compare a saída com a tabela esperada abaixo, conferida na revisão rodando o mesmo script no
repositório do GitHub. Se alguma linha for diferente, pare e mostre a diferença ao usuário.

| Passo | Commit de teste | Resultado no commit de teste | Commit de código | Resultado no commit de código |
|---|---|---|---|---|
| CT01 | `9445f38` test: CT01 atraso abaixo da tolerância não gera crédito | 1 erro | `da797f4` feat: calcula crédito zero dentro da tolerância | 1 passou |
| CT02 e CT03 | `a6259a7` test: CT02 e CT03 limite de 2 h do Varejo | 1 falhou, 2 passaram | `c5cdb56` feat: aplica 10% do frete acima de 2 h no Varejo | 3 passaram |
| CT10 | `a49f71d` test: CT10 arredondamento do crédito ao centavo | 1 falhou, 3 passaram | `17f7f60` feat: arredonda o crédito ao centavo, meio para cima | 4 passaram |
| CT04 e CT05 | `506aff0` test: CT04 e CT05 limite de 24 h do Varejo | 1 falhou, 5 passaram | `cd257cd` feat: aplica 25% do frete acima de 24 h no Varejo | 6 passaram |
| CT06 e CT07 | `3f15408` test: CT06 e CT07 limite de 72 h do Varejo | 1 falhou, 7 passaram | `3f9f750` feat: aplica 50% do frete acima de 72 h no Varejo | 8 passaram |
| CT08 e CT09 | `0080df4` test: CT08 e CT09 teto de R$ 500 do Varejo | 1 falhou, 9 passaram | `ae46758` feat: limita o crédito do Varejo a R$ 500 | 10 passaram |
| CT11 a CT14 | `bef975a` test: CT11 a CT14 percentuais dobrados do Corporativo | 3 falharam, 11 passaram | `dbd1558` feat: dobra os percentuais para o Corporativo | 14 passaram |
| CT15 a CT17 | `61b6044` test: CT15 a CT17 teto de R$ 2.000 do Corporativo | 3 falharam, 14 passaram | `27bfb24` feat: limita o crédito do Corporativo a R$ 2.000 | 17 passaram |
| CT20 | `c845b36` test: CT20 tipo de cliente não suportado gera erro | 1 erro | `becb15b` feat: rejeita tipo de cliente não suportado | 18 passaram |
| CT18 | `ce954a5` test: CT18 Cortesia não recebe crédito | 1 falhou, 18 passaram | `69d4ee7` feat: Cortesia não recebe crédito | 19 passaram |
| CT19 | `1affcfe` test: CT19 novo tipo de cliente sem alterar os existentes | 1 falhou, 19 passaram | `193778d` feat: permite registrar política de crédito para tipo novo | 20 passaram |
| Refatoração | Sem teste novo | Sem teste novo | `bbe403a` refactor: aplica Strategy às políticas de crédito | 20 passaram |
| CT21 e CT22 | `4a512a9` test: CT21 e CT22 apuração do atraso entre prazo e confirmação | 2 falharam, 20 passaram | `be83b3a` feat: apura o atraso em minutos arredondados para cima | 22 passaram |

No fim de `implementacao/README.md`, substitua o parágrafo atual

```
Evidência do TDD: `git log --oneline -- implementacao/` mostra cada commit `test:` antes do
commit `feat:` que o faz passar.
```

por esta seção, com a tabela **gerada pelo script** no lugar indicado:

```markdown
## Evidência do TDD

O histórico (`git log --oneline -- implementacao/`) mostra cada commit `test:` antes do commit
`feat:` que o faz passar. A tabela abaixo foi gerada rodando `python -m pytest` no conteúdo de
`implementacao/` de cada commit, extraído com `git archive`, sem alterar o histórico: todo
commit de teste termina vermelho e o commit de código seguinte termina verde. Em CT01 e CT20, o
vermelho é um erro de importação, porque a classe ou a exceção testada ainda não existia.

<tabela gerada pelo script>
```

Depois, apague o script da pasta temporária.

### 5. Registro da revisão em `docs/05-uso-de-ia.md`

Acrescente estas quatro linhas ao fim da tabela. A linha 1 já tem a decisão informada pelo
usuário. Nas outras, proponha o texto sugerido e confirme com o usuário antes de gravar
(regra 9 do PRD-00).

```markdown
| Revisão final | Ao Claude (chat): revisar o repositório entregue contra os PRDs e os critérios de avaliação | Recriar o repositório com "Use this template", porque o README pede isso e o repositório foi criado como fork | Descartada | O professor autorizou em aula o uso de fork |
| Revisão final | Ao Claude (chat): revisar o repositório entregue contra os PRDs e os critérios de avaliação | Não reescrever o histórico para trocar o autor "Laboratório FIAP", porque isso mudaria o hash de todos os commits, inclusive os de TDD; explicar a autoria no README e configurar o git com o nome da dupla nos commits novos | <resposta da dupla> | <resposta da dupla> |
| Revisão final | Ao Claude (chat): revisar o repositório entregue contra os PRDs e os critérios de avaliação | Descartar as mudanças locais em README.md e .devcontainer/devcontainer.json, que pareciam ser só de fim de linha (CRLF) | <conforme o passo 1> | <conforme o passo 1> |
| Revisão final | Ao Claude (chat): revisar o repositório entregue contra os PRDs e os critérios de avaliação | Documentar no implementacao/README.md o resultado dos testes em cada commit, para a evidência do TDD ficar verificável | <resposta da dupla> | <resposta da dupla> |
```

Textos sugeridos para confirmar com o usuário:

- Linha 2: "Aceita" / "Reescrever o histórico mudaria todos os hashes e a evidência do TDD; a
  observação no README identifica a dupla sem esse risco".
- Linha 3, se no passo 1 os arquivos **não** apareceram como modificados: "Descartada" / "No
  computador da dupla os dois arquivos não estavam modificados: o Git para Windows converte o fim
  de linha, e a diferença só aparecia na cópia em zip aberta em outro sistema".
- Linha 3, se apareceram modificados só no fim de linha: "Aceita" / "A diferença era só de fim de
  linha, sem mudança de conteúdo; commitar poluiria o histórico".
- Linha 4: "Aceita" / "A tabela mostra, commit a commit, que cada teste novo falhou antes do
  código que o fez passar".

Pergunte também se alguma linha anterior da tabela deveria ser "Alterada" ou "Descartada". Só
mude uma linha anterior se o usuário disser o que mudou e por quê.

### 6. Conferência antes dos commits

- [ ] `cd implementacao && python -m pytest -q` continua com 22 testes passando.
- [ ] `git diff --stat` mostra só `README.md` (cerca de 4 linhas novas), `implementacao/README.md`
      e `docs/05-uso-de-ia.md`. Se o `README.md` aparecer com o arquivo inteiro alterado, é fim
      de linha: desfaça e refaça a edição preservando o fim de linha original.
- [ ] Nenhum arquivo de `docs/01` a `docs/04` nem de `implementacao/garantia_prazo/` ou
      `implementacao/tests/` foi alterado.
- [ ] A tabela da evidência do TDD tem 13 linhas de dados e bate com a tabela esperada.
- [ ] Nenhum travessão (—) nos trechos novos.

### 7. Commits e push

Se o usuário informou o e-mail do colega, acrescente a cada commit um segundo `-m` com a linha
de coautoria (o git separa os dois com uma linha em branco, como o GitHub espera):

```
git add README.md implementacao/README.md
git commit -m "docs: documenta a autoria dos commits e a evidência do TDD" -m "Co-authored-by: Thiago Cardoso Mendes Machado <e-mail informado>"
git add docs/05-uso-de-ia.md PRDs/PRD-07-ajustes-da-revisao.md
git commit -m "docs: registra a revisão final no uso de IA" -m "Co-authored-by: Thiago Cardoso Mendes Machado <e-mail informado>"
git push
git log --format="%h %an | %s" -3
```

Sem o e-mail do colega, use os mesmos comandos sem o segundo `-m`.

Os dois commits novos devem aparecer com o nome configurado no passo 2.

### 8. Envio

Mostre a URL do repositório e lembre o usuário de enviar o link pelo formulário do professor.