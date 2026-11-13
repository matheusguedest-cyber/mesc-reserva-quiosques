
from datetime import date

import pytest

from app.extensions import db
from app.models import Quiosque, Reserva
from app.services.reservas import cancelar_reserva, ErroReserva


@pytest.fixture
def reserva_teste(app):
    """
    Cria uma reserva confirmada para o associado 101.
    """

    with app.app_context():

        quiosque = Quiosque(
            numero="01",
            capacidade=10,
            status="ativo"
        )

        db.session.add(quiosque)
        db.session.flush()

        reserva = Reserva(
            id_associado=101,
            id_quiosque=quiosque.id_quiosque,
            data_reserva=date(2026, 11, 20),
            status="confirmada"
        )

        db.session.add(reserva)
        db.session.commit()

        return reserva.id_reserva


def test_cancelamento_antecipado(
    app, reserva_teste, monkeypatch
):
    """
    Permite cancelar antes do dia anterior.
    """

    monkeypatch.setattr(
        "app.services.janela_reservas.obter_data_atual",
        lambda: date(2026, 11, 18)
    )

    with app.app_context():

        reserva = cancelar_reserva(reserva_teste, 101)

        assert reserva.status == "cancelada"

        reserva_banco = db.session.get(
            Reserva,
            reserva_teste
        )

        assert reserva_banco.status == "cancelada"


def test_cancelamento_no_dia_anterior(
    app, reserva_teste, monkeypatch
):
    """
    Permite cancelar até o dia anterior.
    """

    monkeypatch.setattr(
        "app.services.janela_reservas.obter_data_atual",
        lambda: date(2026, 11, 19)
    )

    with app.app_context():

        reserva = cancelar_reserva(reserva_teste, 101)

        assert reserva.status == "cancelada"


def test_impedir_cancelamento_no_proprio_dia(
    app, reserva_teste, monkeypatch
):
    """
    Bloqueia cancelamento no dia da reserva.
    """

    monkeypatch.setattr(
        "app.services.janela_reservas.obter_data_atual",
        lambda: date(2026, 11, 20)
    )

    with app.app_context():

        with pytest.raises(
            ErroReserva,
            match="até o dia anterior"
        ):
            cancelar_reserva(reserva_teste, 101)

        reserva = db.session.get(Reserva, reserva_teste)

        assert reserva.status == "confirmada"


def test_impedir_cancelamento_apos_data(
    app, reserva_teste, monkeypatch
):
    """
    Bloqueia cancelamento após a data reservada.
    """

    monkeypatch.setattr(
        "app.services.janela_reservas.obter_data_atual",
        lambda: date(2026, 11, 21)
    )

    with app.app_context():

        with pytest.raises(
            ErroReserva,
            match="até o dia anterior"
        ):
            cancelar_reserva(reserva_teste, 101)

        reserva = db.session.get(Reserva, reserva_teste)

        assert reserva.status == "confirmada"


def test_impedir_cancelamento_de_outro_associado(
    app, reserva_teste, monkeypatch
):
    """
    Impede cancelar reserva de outro associado.
    """

    monkeypatch.setattr(
        "app.services.janela_reservas.obter_data_atual",
        lambda: date(2026, 11, 18)
    )

    with app.app_context():

        with pytest.raises(
            ErroReserva,
            match="não possui permissão"
        ):
            cancelar_reserva(reserva_teste, 102)

        reserva = db.session.get(Reserva, reserva_teste)

        assert reserva.status == "confirmada"


def test_impedir_cancelamento_duplicado(
    app, reserva_teste, monkeypatch
):
    """
    Impede cancelar reserva já cancelada.
    """

    monkeypatch.setattr(
        "app.services.janela_reservas.obter_data_atual",
        lambda: date(2026, 11, 18)
    )

    with app.app_context():

        cancelar_reserva(reserva_teste, 101)

        with pytest.raises(
            ErroReserva,
            match="não está confirmada"
        ):
            cancelar_reserva(reserva_teste, 101)


def test_impedir_cancelamento_reserva_inexistente(app):
    """
    Impede cancelar uma reserva inexistente.
    """

    with app.app_context():

        with pytest.raises(
            ErroReserva,
            match="Reserva não encontrada"
        ):
            cancelar_reserva(99999, 101)
