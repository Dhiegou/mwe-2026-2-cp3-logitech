from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class Atraso:
    minutos: int

    @classmethod
    def de(cls, horas: int = 0, minutos: int = 0) -> "Atraso":
        return cls(horas * 60 + minutos)

    @classmethod
    def entre(cls, prazo_prometido: datetime, confirmada_em: datetime) -> "Atraso":
        """Minutos entre o prazo e a confirmação, arredondados para cima; antecipada = 0."""
        diferenca = confirmada_em - prazo_prometido
        if diferenca <= timedelta(0):
            return cls(0)
        minutos, resto = divmod(diferenca, timedelta(minutes=1))
        return cls(minutos + (1 if resto else 0))
