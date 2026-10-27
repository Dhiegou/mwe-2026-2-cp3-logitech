from decimal import Decimal

from garantia_prazo import Atraso, CalculadoraDeCredito

calculadora = CalculadoraDeCredito.padrao()


def credito_varejo(frete: str, horas: int, minutos: int = 0) -> Decimal:
    return calculadora.calcular("VAREJO", Decimal(frete), Atraso.de(horas=horas, minutos=minutos))


def test_ct01_atraso_abaixo_da_tolerancia_nao_gera_credito():
    assert credito_varejo("300.00", 1, 59) == Decimal("0.00")


def test_ct02_atraso_de_exatamente_2h_nao_gera_credito():
    assert credito_varejo("300.00", 2, 0) == Decimal("0.00")


def test_ct03_atraso_logo_acima_de_2h_gera_10_por_cento():
    assert credito_varejo("300.00", 2, 1) == Decimal("30.00")


def test_ct10_credito_arredondado_ao_centavo_meio_para_cima():
    assert credito_varejo("123.45", 2, 1) == Decimal("12.35")
