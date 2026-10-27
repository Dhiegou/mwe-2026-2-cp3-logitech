from decimal import Decimal

from garantia_prazo import Atraso, CalculadoraDeCredito

calculadora = CalculadoraDeCredito.padrao()


def credito_varejo(frete: str, horas: int, minutos: int = 0) -> Decimal:
    return calculadora.calcular("VAREJO", Decimal(frete), Atraso.de(horas=horas, minutos=minutos))


def test_ct01_atraso_abaixo_da_tolerancia_nao_gera_credito():
    assert credito_varejo("300.00", 1, 59) == Decimal("0.00")
