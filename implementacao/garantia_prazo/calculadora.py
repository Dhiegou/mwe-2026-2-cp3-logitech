from decimal import Decimal

from .atraso import Atraso


class CalculadoraDeCredito:
    @classmethod
    def padrao(cls) -> "CalculadoraDeCredito":
        return cls()

    def calcular(self, tipo_cliente: str, valor_frete: Decimal, atraso: Atraso) -> Decimal:
        if atraso.minutos > 120:
            return valor_frete * Decimal("0.10")
        return Decimal("0.00")
