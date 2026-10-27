from decimal import Decimal

import pytest

from garantia_prazo import Atraso, CalculadoraDeCredito, TipoDeClienteNaoSuportado


def test_ct20_tipo_de_cliente_nao_registrado_gera_erro():
    calculadora = CalculadoraDeCredito.padrao()
    with pytest.raises(TipoDeClienteNaoSuportado):
        calculadora.calcular("ATACADO", Decimal("300.00"), Atraso.de(horas=5))


class PoliticaStub:
    """Dublê do tipo Stub: devolve um crédito fixo, sem regra própria."""

    def calcular(self, valor_frete: Decimal, atraso: Atraso) -> Decimal:
        return Decimal("42.00")


def test_ct19_novo_tipo_de_cliente_entra_sem_alterar_os_existentes():
    calculadora = CalculadoraDeCredito.padrao().com_politica("PREMIUM", PoliticaStub())

    assert calculadora.calcular("PREMIUM", Decimal("300.00"), Atraso.de(horas=5)) == Decimal("42.00")
    assert calculadora.calcular("VAREJO", Decimal("300.00"), Atraso.de(horas=2, minutos=1)) == Decimal("30.00")
    assert calculadora.calcular("CORPORATIVO", Decimal("300.00"), Atraso.de(horas=2, minutos=1)) == Decimal("60.00")
