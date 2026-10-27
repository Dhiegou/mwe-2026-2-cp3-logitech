from decimal import Decimal

from .atraso import Atraso


class CalculadoraDeCredito:
    @classmethod
    def padrao(cls) -> "CalculadoraDeCredito":
        return cls()

    def calcular(self, tipo_cliente: str, valor_frete: Decimal, atraso: Atraso) -> Decimal:
        return Decimal("0.00")
