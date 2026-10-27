from dataclasses import dataclass


@dataclass(frozen=True)
class Atraso:
    minutos: int

    @classmethod
    def de(cls, horas: int = 0, minutos: int = 0) -> "Atraso":
        return cls(horas * 60 + minutos)
