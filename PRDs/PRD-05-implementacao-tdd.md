# PRD-05 · Implementação em TDD (`implementacao/`)

> Pré-requisito: PRD-04 executado. Siga as regras gerais do `PRDs/PRD-00-visao-geral.md`.
> Linguagem: **Python 3.10+ com pytest** (decisão D4 do PRD-00).

## Objetivo

Implementar a regra de cálculo do crédito (RF02, RF03 e RF04) em TDD, com o histórico de
commits mostrando cada teste **antes** do código que o faz passar, e registrar a execução em
`implementacao/README.md`.

## Critério de avaliação que este PRD atende

> "Testes escritos antes do código, visíveis no histórico de commits; testes executando e
> passando; regras do RF02 ao RF04 cobertas."

## Regras do ciclo (obrigatórias)

1. **Vermelho:** acrescente só os testes do passo, rode `python -m pytest` e confirme que algum
   teste novo **falha** (falha de asserção ou erro de importação contam). Mostre ao usuário a
   linha do resumo do pytest. Faça o commit **só dos arquivos de teste** com a mensagem `test:`
   do passo.
2. **Verde:** escreva o **mínimo** de código de produção que faz os testes passarem. Rode a
   suíte inteira e confirme que tudo passa. Faça o commit **só do código de produção** com a
   mensagem `feat:` do passo.
3. **Não antecipe passos.** Não escreva código para casos que ainda não têm teste. Em especial:
   não arredonde antes do passo 3, não implemente o teto do Corporativo antes do passo 8, não
   trate o tipo Cortesia antes do passo 10, não crie o registro de políticas antes do passo 11.
   A ordem dos passos foi testada para que cada passo comece vermelho; se um passo novo passar
   sem mudança de código, pare e avise o usuário, não "force" uma falha.
4. Não altere testes de passos anteriores. Não use `float` para dinheiro: use `Decimal`.
5. Commits um a um, na ordem, sem `--amend`. Faça push ao fim de cada passo verde (assim o
   histórico fica salvo mesmo se o tempo acabar).
6. Os testes usam os IDs do `docs/03-testes.md` no nome da função (`test_ct01_...`).

## Plano de corte por tempo

Prioridade: passos 0 a 11 cobrem RF02, RF03 e RF04 (necessários para a nota máxima). O passo 12
(refatoração para Strategy) é o próximo em importância. O passo 13 (RF01) é opcional. Se faltar
tempo, pare depois de qualquer passo verde já com commit e vá direto ao passo 14 (registro).

## Passo 0 · Configuração do projeto

Antes: `python --version` deve ser 3.10 ou maior (no Codespace do repositório já é). Se não
houver Python, pare e avise o usuário.

Crie estes arquivos:

`implementacao/requirements-dev.txt`
```
pytest>=8
```

`implementacao/pyproject.toml`
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
addopts = "-v"
```

`implementacao/.gitignore`
```
__pycache__/
.pytest_cache/
.venv/
```

`implementacao/garantia_prazo/__init__.py` vazio e a pasta `implementacao/tests/` (sem
`__init__.py`).

Instale o pytest: `cd implementacao && python -m pip install -r requirements-dev.txt`. Se o pip
recusar por ambiente gerenciado, crie um ambiente virtual (`python -m venv .venv`, ative-o e
repita). Todos os comandos de teste deste PRD rodam dentro de `implementacao/`.

Commit: `chore: configura projeto Python com pytest`

## Estrutura alvo do código de produção

- `garantia_prazo/atraso.py`: objeto de valor `Atraso` (`@dataclass(frozen=True)` com o campo
  `minutos: int` e o método de classe `de(horas=0, minutos=0)`).
- `garantia_prazo/calculadora.py`: `CalculadoraDeCredito` (método de classe `padrao()` e método
  `calcular(tipo_cliente: str, valor_frete: Decimal, atraso: Atraso) -> Decimal`) e, a partir do
  passo 9, a exceção `TipoDeClienteNaoSuportado`.
- `garantia_prazo/politicas.py`: criado só no passo 12 (refatoração).
- `garantia_prazo/__init__.py`: reexporta `Atraso`, `CalculadoraDeCredito` e, a partir do passo
  9, `TipoDeClienteNaoSuportado`.

Tipos de cliente são strings: `"VAREJO"`, `"CORPORATIVO"`, `"CORTESIA"`.

## Passos do ciclo

### Passo 1 · CT01

Crie `tests/test_credito_varejo.py`:

```python
from decimal import Decimal

from garantia_prazo import Atraso, CalculadoraDeCredito

calculadora = CalculadoraDeCredito.padrao()


def credito_varejo(frete: str, horas: int, minutos: int = 0) -> Decimal:
    return calculadora.calcular("VAREJO", Decimal(frete), Atraso.de(horas=horas, minutos=minutos))


def test_ct01_atraso_abaixo_da_tolerancia_nao_gera_credito():
    assert credito_varejo("300.00", 1, 59) == Decimal("0.00")
```

- Vermelho esperado: erro de importação (`Atraso` e `CalculadoraDeCredito` não existem).
- Commit do teste: `test: CT01 atraso abaixo da tolerância não gera crédito`
- Mínimo esperado: criar `Atraso` e `CalculadoraDeCredito` com `calcular` devolvendo
  `Decimal("0.00")`.
- Commit do código: `feat: calcula crédito zero dentro da tolerância`

### Passo 2 · CT02 e CT03 (limite de 2 h)

Acrescente ao fim de `tests/test_credito_varejo.py`:

```python
def test_ct02_atraso_de_exatamente_2h_nao_gera_credito():
    assert credito_varejo("300.00", 2, 0) == Decimal("0.00")


def test_ct03_atraso_logo_acima_de_2h_gera_10_por_cento():
    assert credito_varejo("300.00", 2, 1) == Decimal("30.00")
```

- Vermelho esperado: CT03 falha (recebe 0,00).
- Commit do teste: `test: CT02 e CT03 limite de 2 h do Varejo`
- Mínimo esperado: acima de 120 minutos, devolver `valor_frete * Decimal("0.10")` (sem
  arredondar).
- Commit do código: `feat: aplica 10% do frete acima de 2 h no Varejo`

### Passo 3 · CT10 (arredondamento)

Acrescente:

```python
def test_ct10_credito_arredondado_ao_centavo_meio_para_cima():
    assert credito_varejo("123.45", 2, 1) == Decimal("12.35")
```

- Vermelho esperado: CT10 falha (recebe 12.3450).
- Commit do teste: `test: CT10 arredondamento do crédito ao centavo`
- Mínimo esperado: `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- Commit do código: `feat: arredonda o crédito ao centavo, meio para cima`

### Passo 4 · CT04 e CT05 (limite de 24 h)

Acrescente:

```python
def test_ct04_atraso_de_exatamente_24h_continua_em_10_por_cento():
    assert credito_varejo("300.00", 24, 0) == Decimal("30.00")


def test_ct05_atraso_logo_acima_de_24h_gera_25_por_cento():
    assert credito_varejo("300.00", 24, 1) == Decimal("75.00")
```

- Vermelho esperado: CT05 falha (recebe 30.00).
- Commit do teste: `test: CT04 e CT05 limite de 24 h do Varejo`
- Commit do código: `feat: aplica 25% do frete acima de 24 h no Varejo`

### Passo 5 · CT06 e CT07 (limite de 72 h)

Acrescente:

```python
def test_ct06_atraso_de_exatamente_72h_continua_em_25_por_cento():
    assert credito_varejo("300.00", 72, 0) == Decimal("75.00")


def test_ct07_atraso_logo_acima_de_72h_gera_50_por_cento():
    assert credito_varejo("300.00", 72, 1) == Decimal("150.00")
```

- Vermelho esperado: CT07 falha (recebe 75.00).
- Commit do teste: `test: CT06 e CT07 limite de 72 h do Varejo`
- Commit do código: `feat: aplica 50% do frete acima de 72 h no Varejo`

### Passo 6 · CT08 e CT09 (teto do Varejo)

Acrescente:

```python
def test_ct08_credito_igual_ao_teto_de_500_e_mantido():
    assert credito_varejo("1000.00", 72, 1) == Decimal("500.00")


def test_ct09_credito_um_centavo_acima_do_teto_e_limitado_a_500():
    assert credito_varejo("1000.02", 72, 1) == Decimal("500.00")
```

- Vermelho esperado: CT09 falha (recebe 500.01).
- Commit do teste: `test: CT08 e CT09 teto de R$ 500 do Varejo`
- Mínimo esperado: `min(credito, Decimal("500.00"))` antes do arredondamento.
- Commit do código: `feat: limita o crédito do Varejo a R$ 500`

### Passo 7 · CT11 a CT14 (percentuais do Corporativo)

Crie `tests/test_credito_corporativo.py`:

```python
from decimal import Decimal

from garantia_prazo import Atraso, CalculadoraDeCredito

calculadora = CalculadoraDeCredito.padrao()


def credito_corporativo(frete: str, horas: int, minutos: int = 0) -> Decimal:
    return calculadora.calcular("CORPORATIVO", Decimal(frete), Atraso.de(horas=horas, minutos=minutos))


def test_ct11_corporativo_mantem_a_tolerancia_de_2h():
    assert credito_corporativo("300.00", 2, 0) == Decimal("0.00")


def test_ct12_corporativo_acima_de_2h_gera_20_por_cento():
    assert credito_corporativo("300.00", 2, 1) == Decimal("60.00")


def test_ct13_corporativo_acima_de_24h_gera_50_por_cento():
    assert credito_corporativo("300.00", 24, 1) == Decimal("150.00")


def test_ct14_corporativo_acima_de_72h_gera_100_por_cento():
    assert credito_corporativo("300.00", 72, 1) == Decimal("300.00")
```

- Vermelho esperado: CT12, CT13 e CT14 falham (recebem os valores do Varejo).
- Commit do teste: `test: CT11 a CT14 percentuais dobrados do Corporativo`
- Mínimo esperado: multiplicar o percentual por 2 quando o tipo for `"CORPORATIVO"`. **Mantenha
  o teto de R$ 500 para todos neste passo.**
- Commit do código: `feat: dobra os percentuais para o Corporativo`

### Passo 8 · CT15 a CT17 (teto do Corporativo)

Acrescente ao fim de `tests/test_credito_corporativo.py`:

```python
def test_ct15_corporativo_acima_do_teto_do_varejo_nao_fica_limitado_a_500():
    assert credito_corporativo("1500.00", 72, 1) == Decimal("1500.00")


def test_ct16_corporativo_igual_ao_teto_de_2000_e_mantido():
    assert credito_corporativo("2000.00", 72, 1) == Decimal("2000.00")


def test_ct17_corporativo_um_centavo_acima_do_teto_e_limitado_a_2000():
    assert credito_corporativo("2000.01", 72, 1) == Decimal("2000.00")
```

- Vermelho esperado: os três falham (recebem 500.00).
- Commit do teste: `test: CT15 a CT17 teto de R$ 2.000 do Corporativo`
- Commit do código: `feat: limita o crédito do Corporativo a R$ 2.000`

### Passo 9 · CT20 (tipo não suportado)

Crie `tests/test_tipos_de_cliente.py`:

```python
from decimal import Decimal

import pytest

from garantia_prazo import Atraso, CalculadoraDeCredito, TipoDeClienteNaoSuportado


def test_ct20_tipo_de_cliente_nao_registrado_gera_erro():
    calculadora = CalculadoraDeCredito.padrao()
    with pytest.raises(TipoDeClienteNaoSuportado):
        calculadora.calcular("ATACADO", Decimal("300.00"), Atraso.de(horas=5))
```

- Vermelho esperado: erro de importação (`TipoDeClienteNaoSuportado` não existe).
- Commit do teste: `test: CT20 tipo de cliente não suportado gera erro`
- Mínimo esperado: criar a exceção, exportá-la no `__init__.py` e lançá-la para qualquer tipo
  diferente de `"VAREJO"` e `"CORPORATIVO"`.
- Commit do código: `feat: rejeita tipo de cliente não suportado`

### Passo 10 · CT18 (Cortesia)

Crie `tests/test_credito_cortesia.py`:

```python
from decimal import Decimal

from garantia_prazo import Atraso, CalculadoraDeCredito


def test_ct18_cortesia_nao_recebe_credito():
    calculadora = CalculadoraDeCredito.padrao()
    assert calculadora.calcular("CORTESIA", Decimal("0.00"), Atraso.de(horas=72, minutos=1)) == Decimal("0.00")
```

- Vermelho esperado: CT18 falha com `TipoDeClienteNaoSuportado`.
- Commit do teste: `test: CT18 Cortesia não recebe crédito`
- Commit do código: `feat: Cortesia não recebe crédito`

### Passo 11 · CT19 (tipo novo sem alterar os existentes, RF04)

Acrescente ao fim de `tests/test_tipos_de_cliente.py`:

```python
class PoliticaStub:
    """Dublê do tipo Stub: devolve um crédito fixo, sem regra própria."""

    def calcular(self, valor_frete: Decimal, atraso: Atraso) -> Decimal:
        return Decimal("42.00")


def test_ct19_novo_tipo_de_cliente_entra_sem_alterar_os_existentes():
    calculadora = CalculadoraDeCredito.padrao().com_politica("PREMIUM", PoliticaStub())

    assert calculadora.calcular("PREMIUM", Decimal("300.00"), Atraso.de(horas=5)) == Decimal("42.00")
    assert calculadora.calcular("VAREJO", Decimal("300.00"), Atraso.de(horas=2, minutos=1)) == Decimal("30.00")
    assert calculadora.calcular("CORPORATIVO", Decimal("300.00"), Atraso.de(horas=2, minutos=1)) == Decimal("60.00")
```

- Vermelho esperado: CT19 falha (`com_politica` não existe).
- Commit do teste: `test: CT19 novo tipo de cliente sem alterar os existentes`
- Mínimo esperado: `com_politica(tipo_cliente, politica)` devolve uma **nova** calculadora que
  consulta primeiro as políticas registradas e, se o tipo não estiver lá, segue a regra atual.
- Commit do código: `feat: permite registrar política de crédito para tipo novo`

### Passo 12 · Refatoração para Strategy (testes continuam verdes)

Com todos os testes passando, troque os `if` por tipo pela estrutura abaixo. Não altere nenhum
teste. Rode a suíte antes e depois: o número de testes e o resultado devem ser os mesmos.

`garantia_prazo/politicas.py`

```python
"""Políticas de crédito por tipo de cliente (padrão Strategy, RF02 a RF04)."""
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

from .atraso import Atraso

CENTAVO = Decimal("0.01")
SEM_CREDITO = Decimal("0.00")

# Faixas de atraso do RF02: (limite superior em minutos, inclusivo; percentual base)
FAIXAS_DE_ATRASO = (
    (2 * 60, Decimal("0.00")),    # tolerância: até 2 h
    (24 * 60, Decimal("0.10")),   # acima de 2 h até 24 h
    (72 * 60, Decimal("0.25")),   # acima de 24 h até 72 h
)
PERCENTUAL_ACIMA_DE_72H = Decimal("0.50")


def percentual_base(atraso: Atraso) -> Decimal:
    for limite_em_minutos, percentual in FAIXAS_DE_ATRASO:
        if atraso.minutos <= limite_em_minutos:
            return percentual
    return PERCENTUAL_ACIMA_DE_72H


class PoliticaDeCredito(Protocol):
    def calcular(self, valor_frete: Decimal, atraso: Atraso) -> Decimal: ...


@dataclass(frozen=True)
class PoliticaPorFaixaDeAtraso:
    """Varejo (multiplicador 1, teto R$ 500) e Corporativo (multiplicador 2, teto R$ 2.000)."""

    multiplicador: Decimal
    teto: Decimal

    def calcular(self, valor_frete: Decimal, atraso: Atraso) -> Decimal:
        credito = valor_frete * percentual_base(atraso) * self.multiplicador
        return min(credito, self.teto).quantize(CENTAVO, rounding=ROUND_HALF_UP)


class PoliticaSemCredito:
    """Cortesia: nunca gera crédito. O aviso de atraso é responsabilidade de Notificações."""

    def calcular(self, valor_frete: Decimal, atraso: Atraso) -> Decimal:
        return SEM_CREDITO
```

`garantia_prazo/calculadora.py`

```python
"""Escolhe a política do tipo de cliente e delega o cálculo (RF04)."""
from decimal import Decimal
from typing import Mapping

from .atraso import Atraso
from .politicas import PoliticaDeCredito, PoliticaPorFaixaDeAtraso, PoliticaSemCredito


class TipoDeClienteNaoSuportado(Exception):
    """Tipo sem política registrada: nunca devolve crédito zero em silêncio."""


POLITICAS_PADRAO: Mapping[str, PoliticaDeCredito] = {
    "VAREJO": PoliticaPorFaixaDeAtraso(multiplicador=Decimal("1"), teto=Decimal("500.00")),
    "CORPORATIVO": PoliticaPorFaixaDeAtraso(multiplicador=Decimal("2"), teto=Decimal("2000.00")),
    "CORTESIA": PoliticaSemCredito(),
}


class CalculadoraDeCredito:
    def __init__(self, politicas: Mapping[str, PoliticaDeCredito]):
        self._politicas = dict(politicas)

    @classmethod
    def padrao(cls) -> "CalculadoraDeCredito":
        return cls(POLITICAS_PADRAO)

    def com_politica(self, tipo_cliente: str, politica: PoliticaDeCredito) -> "CalculadoraDeCredito":
        """Nova calculadora com o tipo novo; as políticas existentes não mudam."""
        return CalculadoraDeCredito({**self._politicas, tipo_cliente: politica})

    def calcular(self, tipo_cliente: str, valor_frete: Decimal, atraso: Atraso) -> Decimal:
        politica = self._politicas.get(tipo_cliente)
        if politica is None:
            raise TipoDeClienteNaoSuportado(tipo_cliente)
        return politica.calcular(valor_frete, atraso)
```

`garantia_prazo/__init__.py`

```python
from .atraso import Atraso
from .calculadora import CalculadoraDeCredito, TipoDeClienteNaoSuportado
from .politicas import PoliticaDeCredito, PoliticaPorFaixaDeAtraso, PoliticaSemCredito

__all__ = [
    "Atraso",
    "CalculadoraDeCredito",
    "TipoDeClienteNaoSuportado",
    "PoliticaDeCredito",
    "PoliticaPorFaixaDeAtraso",
    "PoliticaSemCredito",
]
```

Commit: `refactor: aplica Strategy às políticas de crédito`

### Passo 13 (opcional) · CT21 e CT22 (apuração do atraso, RF01)

Crie `tests/test_atraso.py`:

```python
from datetime import datetime

from garantia_prazo import Atraso


def test_ct21_entrega_antecipada_tem_atraso_zero():
    prazo = datetime(2026, 11, 10, 14, 0)
    confirmacao = datetime(2026, 11, 10, 13, 30)
    assert Atraso.entre(prazo, confirmacao) == Atraso(minutos=0)


def test_ct22_fracao_de_minuto_conta_como_minuto_iniciado():
    prazo = datetime(2026, 11, 10, 14, 0)
    confirmacao = datetime(2026, 11, 10, 16, 0, 30)
    assert Atraso.entre(prazo, confirmacao) == Atraso(minutos=121)
```

- Vermelho esperado: os dois falham (`Atraso.entre` não existe).
- Commit do teste: `test: CT21 e CT22 apuração do atraso entre prazo e confirmação`
- Código esperado em `garantia_prazo/atraso.py` (acrescente
  `from datetime import datetime, timedelta` no topo do arquivo e este método na classe
  `Atraso`):

```python
    @classmethod
    def entre(cls, prazo_prometido: datetime, confirmada_em: datetime) -> "Atraso":
        """Minutos entre o prazo e a confirmação, arredondados para cima; antecipada = 0."""
        diferenca = confirmada_em - prazo_prometido
        if diferenca <= timedelta(0):
            return cls(0)
        minutos, resto = divmod(diferenca, timedelta(minutes=1))
        return cls(minutos + (1 if resto else 0))
```

- Commit do código: `feat: apura o atraso em minutos arredondados para cima`

### Passo 14 · Registro em `implementacao/README.md`

Rode `python -m pytest` dentro de `implementacao/` e preencha a seção "O que registrar aqui",
apagando o comentário `<!-- Preencham ao final. -->`:

- Linguagem e framework de teste: Python 3 (versão de `python --version`) com pytest (versão
  de `python -m pytest --version`).
- Comando para executar os testes:
  `cd implementacao && python -m pip install -r requirements-dev.txt && python -m pytest`
- Casos do plano implementados (IDs): CT01 a CT20 (RF02, RF03 e RF04); acrescente CT21 e CT22
  (RF01) se o passo 13 foi feito.
- Saída da última execução dos testes: cole a saída **real** do pytest no bloco de código, no
  lugar de `cole aqui a saída`. Não invente nem resuma a saída.

Se der tempo, acrescente ao fim do README uma linha "Evidência do TDD" com o comando
`git log --oneline -- implementacao/` para o professor ver os pares `test:` e `feat:`.

Commit: `docs: registra a execução dos testes da implementação` e push.

## Critérios de aceite

- [ ] `python -m pytest` dentro de `implementacao/` passa com 20 testes (22 com o passo 13).
- [ ] `git log --oneline -- implementacao/` mostra, para cada passo, o commit `test:` antes do
      commit `feat:` correspondente.
- [ ] Nenhum `__pycache__`, `.pytest_cache` ou `.venv` versionado.
- [ ] `implementacao/README.md` preenchido com a saída real.

## Registro de uso de IA (`docs/05-uso-de-ia.md`)

Acrescente esta linha ao fim da tabela, com as duas últimas colunas preenchidas pela dupla:

```markdown
| 5. Implementação em TDD | Ao Claude (chat): planejar os ciclos de TDD em PRD; ao Claude Code: executar os ciclos, rodando os testes e fazendo os commits | Python com pytest; ordem dos passos pensada para cada teste novo falhar antes do código (o arredondamento antes das faixas, o erro de tipo desconhecido antes da Cortesia); `Decimal` para dinheiro; refatoração final para Strategy com `PoliticaPorFaixaDeAtraso` e `PoliticaSemCredito` | <resposta da dupla> | <resposta da dupla> |
```

Commit dessa linha junto com o passo 14.
