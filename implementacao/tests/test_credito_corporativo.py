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
