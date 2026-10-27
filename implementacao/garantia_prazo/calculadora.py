"""Escolhe a política do tipo de cliente e delega o cálculo (RF04)."""
from decimal import Decimal
from typing import Mapping

from .atraso import Atraso
from .politicas import PoliticaDeCredito, PoliticaPorFaixaDeAtraso, PoliticaSemCredito


class TipoDeClienteNaoSuportado(Exception):
    """Tipo sem política registrada: nunca devolve crédito zero em silêncio."""


POLITICAS_PADRAO: Mapping[str, PoliticaDeCredito] = {
    "VAREJO": PoliticaPorFaixaDeAtraso(multiplicador=Decimal("1"), teto=Decimal("500.00")),
    "CORPORATIVO": PoliticaPorFaixaDeAtraso(multiplicador=Decimal("2"), teto=Decimal("2000.00")),
    "CORTESIA": PoliticaSemCredito(),
}


class CalculadoraDeCredito:
    def __init__(self, politicas: Mapping[str, PoliticaDeCredito]):
        self._politicas = dict(politicas)

    @classmethod
    def padrao(cls) -> "CalculadoraDeCredito":
        return cls(POLITICAS_PADRAO)

    def com_politica(self, tipo_cliente: str, politica: PoliticaDeCredito) -> "CalculadoraDeCredito":
        """Nova calculadora com o tipo novo; as políticas existentes não mudam."""
        return CalculadoraDeCredito({**self._politicas, tipo_cliente: politica})

    def calcular(self, tipo_cliente: str, valor_frete: Decimal, atraso: Atraso) -> Decimal:
        politica = self._politicas.get(tipo_cliente)
        if politica is None:
            raise TipoDeClienteNaoSuportado(tipo_cliente)
        return politica.calcular(valor_frete, atraso)
