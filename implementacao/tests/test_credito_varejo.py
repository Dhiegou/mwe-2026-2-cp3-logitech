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


def test_ct04_atraso_de_exatamente_24h_continua_em_10_por_cento():
    assert credito_varejo("300.00", 24, 0) == Decimal("30.00")


def test_ct05_atraso_logo_acima_de_24h_gera_25_por_cento():
    assert credito_varejo("300.00", 24, 1) == Decimal("75.00")


def test_ct06_atraso_de_exatamente_72h_continua_em_25_por_cento():
    assert credito_varejo("300.00", 72, 0) == Decimal("75.00")


def test_ct07_atraso_logo_acima_de_72h_gera_50_por_cento():
    assert credito_varejo("300.00", 72, 1) == Decimal("150.00")


def test_ct08_credito_igual_ao_teto_de_500_e_mantido():
    assert credito_varejo("1000.00", 72, 1) == Decimal("500.00")


def test_ct09_credito_um_centavo_acima_do_teto_e_limitado_a_500():
    assert credito_varejo("1000.02", 72, 1) == Decimal("500.00")
