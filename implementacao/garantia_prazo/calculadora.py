from decimal import ROUND_HALF_UP, Decimal

from .atraso import Atraso


class TipoDeClienteNaoSuportado(Exception):
    pass


class CalculadoraDeCredito:
    def __init__(self, politicas=None):
        self._politicas = dict(politicas or {})

    @classmethod
    def padrao(cls) -> "CalculadoraDeCredito":
        return cls()

    def com_politica(self, tipo_cliente: str, politica) -> "CalculadoraDeCredito":
        return CalculadoraDeCredito({**self._politicas, tipo_cliente: politica})

    def calcular(self, tipo_cliente: str, valor_frete: Decimal, atraso: Atraso) -> Decimal:
        if tipo_cliente in self._politicas:
            return self._politicas[tipo_cliente].calcular(valor_frete, atraso)
        if tipo_cliente == "CORTESIA":
            return Decimal("0.00")
        if tipo_cliente not in ("VAREJO", "CORPORATIVO"):
            raise TipoDeClienteNaoSuportado(tipo_cliente)
        if atraso.minutos > 4320:
            percentual = Decimal("0.50")
        elif atraso.minutos > 1440:
            percentual = Decimal("0.25")
        elif atraso.minutos > 120:
            percentual = Decimal("0.10")
        else:
            percentual = Decimal("0.00")
        teto = Decimal("500.00")
        if tipo_cliente == "CORPORATIVO":
            percentual = percentual * 2
            teto = Decimal("2000.00")
        return min(valor_frete * percentual, teto).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
