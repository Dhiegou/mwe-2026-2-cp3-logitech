from decimal import ROUND_HALF_UP, Decimal

from .atraso import Atraso


class CalculadoraDeCredito:
    @classmethod
    def padrao(cls) -> "CalculadoraDeCredito":
        return cls()

    def calcular(self, tipo_cliente: str, valor_frete: Decimal, atraso: Atraso) -> Decimal:
        if atraso.minutos > 4320:
            percentual = Decimal("0.50")
        elif atraso.minutos > 1440:
            percentual = Decimal("0.25")
        elif atraso.minutos > 120:
            percentual = Decimal("0.10")
        else:
            percentual = Decimal("0.00")
        return (valor_frete * percentual).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
