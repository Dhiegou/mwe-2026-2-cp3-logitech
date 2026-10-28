# 5. Implementação em TDD

Implementem a regra de cálculo do crédito (RF02, RF03 e RF04) em **uma** linguagem à
escolha da dupla: Java, C#, Python ou TypeScript. O Codespace deste repositório já traz
as quatro.

## Como trabalhar

1. Escrevam um teste para um caso do plano (`docs/03-testes.md`) e confirmem que ele
   **falha**. Façam o commit: `test: CT01 atraso abaixo da tolerância não gera crédito`.
2. Escrevam o mínimo de código que faz o teste passar. Façam o commit:
   `feat: calcula crédito zero dentro da tolerância`.
3. Se for preciso, refatorem com os testes passando. Façam o commit: `refactor: ...`.
4. Repitam para o próximo caso.

O histórico de commits é a evidência do TDD: o commit de teste vem antes do commit de
código que o faz passar.

## O que registrar aqui

- Linguagem e framework de teste: Python 3.14.6 com pytest 9.2.0
- Comando para executar os testes:
  `cd implementacao && python -m pip install -r requirements-dev.txt && python -m pytest`
- Casos do plano implementados (IDs): CT01 a CT20 (RF02, RF03 e RF04) e CT21 e CT22 (RF01)
- Saída da última execução dos testes:

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.2.0, pluggy-1.7.0 -- C:\Python314\python.exe
cachedir: .pytest_cache
rootdir: D:\CP03\mwe-2026-2-cp3-logitech\implementacao
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.13.0, langsmith-0.8.5
collecting ... collected 22 items

tests/test_atraso.py::test_ct21_entrega_antecipada_tem_atraso_zero PASSED [  4%]
tests/test_atraso.py::test_ct22_fracao_de_minuto_conta_como_minuto_iniciado PASSED [  9%]
tests/test_credito_corporativo.py::test_ct11_corporativo_mantem_a_tolerancia_de_2h PASSED [ 13%]
tests/test_credito_corporativo.py::test_ct12_corporativo_acima_de_2h_gera_20_por_cento PASSED [ 18%]
tests/test_credito_corporativo.py::test_ct13_corporativo_acima_de_24h_gera_50_por_cento PASSED [ 22%]
tests/test_credito_corporativo.py::test_ct14_corporativo_acima_de_72h_gera_100_por_cento PASSED [ 27%]
tests/test_credito_corporativo.py::test_ct15_corporativo_acima_do_teto_do_varejo_nao_fica_limitado_a_500 PASSED [ 31%]
tests/test_credito_corporativo.py::test_ct16_corporativo_igual_ao_teto_de_2000_e_mantido PASSED [ 36%]
tests/test_credito_corporativo.py::test_ct17_corporativo_um_centavo_acima_do_teto_e_limitado_a_2000 PASSED [ 40%]
tests/test_credito_cortesia.py::test_ct18_cortesia_nao_recebe_credito PASSED [ 45%]
tests/test_credito_varejo.py::test_ct01_atraso_abaixo_da_tolerancia_nao_gera_credito PASSED [ 50%]
tests/test_credito_varejo.py::test_ct02_atraso_de_exatamente_2h_nao_gera_credito PASSED [ 54%]
tests/test_credito_varejo.py::test_ct03_atraso_logo_acima_de_2h_gera_10_por_cento PASSED [ 59%]
tests/test_credito_varejo.py::test_ct10_credito_arredondado_ao_centavo_meio_para_cima PASSED [ 63%]
tests/test_credito_varejo.py::test_ct04_atraso_de_exatamente_24h_continua_em_10_por_cento PASSED [ 68%]
tests/test_credito_varejo.py::test_ct05_atraso_logo_acima_de_24h_gera_25_por_cento PASSED [ 72%]
tests/test_credito_varejo.py::test_ct06_atraso_de_exatamente_72h_continua_em_25_por_cento PASSED [ 77%]
tests/test_credito_varejo.py::test_ct07_atraso_logo_acima_de_72h_gera_50_por_cento PASSED [ 81%]
tests/test_credito_varejo.py::test_ct08_credito_igual_ao_teto_de_500_e_mantido PASSED [ 86%]
tests/test_credito_varejo.py::test_ct09_credito_um_centavo_acima_do_teto_e_limitado_a_500 PASSED [ 90%]
tests/test_tipos_de_cliente.py::test_ct20_tipo_de_cliente_nao_registrado_gera_erro PASSED [ 95%]
tests/test_tipos_de_cliente.py::test_ct19_novo_tipo_de_cliente_entra_sem_alterar_os_existentes PASSED [100%]

============================== warnings summary ===============================
C:\Python314\Lib\site-packages\anyio\pytest_plugin.py:14
  C:\Python314\Lib\site-packages\anyio\pytest_plugin.py:14: PytestRemovedIn10Warning: _pytest.python.CallSpec2 has been renamed to CallSpec.
  The CallSpec2 alias will be removed in pytest 10.
  Update imports to use CallSpec instead.
  See https://docs.pytest.org/en/stable/deprecations.html#callspec2-renamed
    from _pytest.python import CallSpec2

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 22 passed, 1 warning in 0.04s ========================
```

## Evidência do TDD

O histórico (`git log --oneline -- implementacao/`) mostra cada commit `test:` antes do commit
`feat:` que o faz passar. A tabela abaixo foi gerada rodando `python -m pytest` no conteúdo de
`implementacao/` de cada commit, extraído com `git archive`, sem alterar o histórico: todo
commit de teste termina vermelho e o commit de código seguinte termina verde. Em CT01 e CT20, o
vermelho é um erro de importação, porque a classe ou a exceção testada ainda não existia.

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
