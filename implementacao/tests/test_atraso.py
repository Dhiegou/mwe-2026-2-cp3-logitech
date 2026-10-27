from datetime import datetime

from garantia_prazo import Atraso


def test_ct21_entrega_antecipada_tem_atraso_zero():
    prazo = datetime(2026, 11, 10, 14, 0)
    confirmacao = datetime(2026, 11, 10, 13, 30)
    assert Atraso.entre(prazo, confirmacao) == Atraso(minutos=0)


def test_ct22_fracao_de_minuto_conta_como_minuto_iniciado():
    prazo = datetime(2026, 11, 10, 14, 0)
    confirmacao = datetime(2026, 11, 10, 16, 0, 30)
    assert Atraso.entre(prazo, confirmacao) == Atraso(minutos=121)
