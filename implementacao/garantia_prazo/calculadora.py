from decimal import ROUND_HALF_UP, Decimal

from .atraso import Atraso


class CalculadoraDeCredito:
    @classmethod
    def padrao(cls) -> "CalculadoraDeCredito":
        return cls()

    def calcular(self, tipo_cliente: str, valor_frete: Decimal, atraso: Atraso) -> Decimal:
        if atraso.minutos > 120:
            return (valor_frete * Decimal("0.10")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return Decimal("0.00")
