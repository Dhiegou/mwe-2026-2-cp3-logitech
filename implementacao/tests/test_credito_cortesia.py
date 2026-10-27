from decimal import Decimal

from garantia_prazo import Atraso, CalculadoraDeCredito


def test_ct18_cortesia_nao_recebe_credito():
    calculadora = CalculadoraDeCredito.padrao()
    assert calculadora.calcular("CORTESIA", Decimal("0.00"), Atraso.de(horas=72, minutos=1)) == Decimal("0.00")
