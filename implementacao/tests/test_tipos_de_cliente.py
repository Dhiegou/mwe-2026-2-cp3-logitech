from decimal import Decimal

import pytest

from garantia_prazo import Atraso, CalculadoraDeCredito, TipoDeClienteNaoSuportado


def test_ct20_tipo_de_cliente_nao_registrado_gera_erro():
    calculadora = CalculadoraDeCredito.padrao()
    with pytest.raises(TipoDeClienteNaoSuportado):
        calculadora.calcular("ATACADO", Decimal("300.00"), Atraso.de(horas=5))
