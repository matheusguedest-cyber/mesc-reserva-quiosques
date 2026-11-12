
from datetime import date

from app.services.janela_reservas import (
    obter_janela_atual,
    validar_data_reserva,
)


def test_segunda_feira_sem_janela():
    assert obter_janela_atual(date(2026, 11, 16)) is None


def test_janela_de_terca_ate_domingo():
    janela = obter_janela_atual(date(2026, 11, 17))

    assert janela == (
        date(2026, 11, 17),
        date(2026, 11, 22),
    )


def test_reserva_permitida_na_terca():
    permitido, erro = validar_data_reserva(
        date(2026, 11, 17),
        date(2026, 11, 17),
    )

    assert permitido is True
    assert erro is None


def test_reserva_permitida_no_domingo():
    permitido, erro = validar_data_reserva(
        date(2026, 11, 22),
        date(2026, 11, 17),
    )

    assert permitido is True
    assert erro is None


def test_reserva_bloqueada_na_segunda():
    permitido, erro = validar_data_reserva(
        date(2026, 11, 20),
        date(2026, 11, 16),
    )

    assert permitido is False
    assert "fechadas" in erro


def test_reserva_fora_da_janela():
    permitido, erro = validar_data_reserva(
        date(2026, 11, 23),
        date(2026, 11, 17),
    )

    assert permitido is False
    assert "fora da janela" in erro


def test_reserva_em_data_passada():
    permitido, erro = validar_data_reserva(
        date(2026, 11, 18),
        date(2026, 11, 20),
    )

    assert permitido is False
    assert "anteriores" in erro


def test_data_invalida():
    permitido, erro = validar_data_reserva(
        "2026-11-20",
        date(2026, 11, 17),
    )

    assert permitido is False
    assert "inválida" in erro
