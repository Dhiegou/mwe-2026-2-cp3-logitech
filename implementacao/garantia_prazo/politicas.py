"""Políticas de crédito por tipo de cliente (padrão Strategy, RF02 a RF04)."""
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

from .atraso import Atraso

CENTAVO = Decimal("0.01")
SEM_CREDITO = Decimal("0.00")

# Faixas de atraso do RF02: (limite superior em minutos, inclusivo; percentual base)
FAIXAS_DE_ATRASO = (
    (2 * 60, Decimal("0.00")),    # tolerância: até 2 h
    (24 * 60, Decimal("0.10")),   # acima de 2 h até 24 h
    (72 * 60, Decimal("0.25")),   # acima de 24 h até 72 h
)
PERCENTUAL_ACIMA_DE_72H = Decimal("0.50")


def percentual_base(atraso: Atraso) -> Decimal:
    for limite_em_minutos, percentual in FAIXAS_DE_ATRASO:
        if atraso.minutos <= limite_em_minutos:
            return percentual
    return PERCENTUAL_ACIMA_DE_72H


class PoliticaDeCredito(Protocol):
    def calcular(self, valor_frete: Decimal, atraso: Atraso) -> Decimal: ...


@dataclass(frozen=True)
class PoliticaPorFaixaDeAtraso:
    """Varejo (multiplicador 1, teto R$ 500) e Corporativo (multiplicador 2, teto R$ 2.000)."""

    multiplicador: Decimal
    teto: Decimal

    def calcular(self, valor_frete: Decimal, atraso: Atraso) -> Decimal:
        credito = valor_frete * percentual_base(atraso) * self.multiplicador
        return min(credito, self.teto).quantize(CENTAVO, rounding=ROUND_HALF_UP)


class PoliticaSemCredito:
    """Cortesia: nunca gera crédito. O aviso de atraso é responsabilidade de Notificações."""

    def calcular(self, valor_frete: Decimal, atraso: Atraso) -> Decimal:
        return SEM_CREDITO
