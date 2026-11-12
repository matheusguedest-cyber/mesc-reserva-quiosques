
from datetime import date, timedelta

import pytest

from app.extensions import db
from app.models import Associado, Quiosque, Reserva
from app.services.reservas import criar_reserva, ErroReserva


@pytest.fixture
def quiosque_teste(app):
    with app.app_context():
        quiosque = Quiosque(
            numero="01",
            capacidade=10,
            status="ativo"
        )

        db.session.add(quiosque)
        db.session.commit()

        return quiosque.id_quiosque


def test_criar_reserva_com_sucesso(app, quiosque_teste):
    with app.app_context():
        data_futura = date.today() + timedelta(days=10)

        reserva = criar_reserva(
            id_associado=101,
            id_quiosque=quiosque_teste,
            data_reserva=data_futura
        )

        assert reserva.id_reserva is not None
        assert reserva.id_associado == 101
        assert reserva.id_quiosque == quiosque_teste
        assert reserva.data_reserva == data_futura
        assert reserva.status == "confirmada"


def test_impedir_reserva_duplicada(app, quiosque_teste):
    with app.app_context():
        data_futura = date.today() + timedelta(days=10)

        criar_reserva(
            id_associado=101,
            id_quiosque=quiosque_teste,
            data_reserva=data_futura
        )

        with pytest.raises(
            ErroReserva,
            match="já está reservado"
        ):
            criar_reserva(
                id_associado=101,
                id_quiosque=quiosque_teste,
                data_reserva=data_futura
            )

        quantidade = db.session.query(Reserva).filter_by(
            id_quiosque=quiosque_teste,
            data_reserva=data_futura,
            status="confirmada"
        ).count()

        assert quantidade == 1


def test_impedir_reserva_data_passada(app, quiosque_teste):
    with app.app_context():
        data_passada = date.today() - timedelta(days=1)

        with pytest.raises(
            ErroReserva,
            match="datas anteriores"
        ):
            criar_reserva(
                id_associado=101,
                id_quiosque=quiosque_teste,
                data_reserva=data_passada
            )


def test_impedir_reserva_quiosque_inativo(app, quiosque_teste):
    with app.app_context():
        quiosque = db.session.get(Quiosque, quiosque_teste)
        quiosque.status = "inativo"
        db.session.commit()

        with pytest.raises(
            ErroReserva,
            match="não está disponível"
        ):
            criar_reserva(
                id_associado=101,
                id_quiosque=quiosque_teste,
                data_reserva=date.today() + timedelta(days=10)
            )


def test_impedir_reserva_associado_inativo(app, quiosque_teste):
    with app.app_context():
        associado = db.session.get(Associado, 101)
        associado.status = "inativo"
        db.session.commit()

        with pytest.raises(
            ErroReserva,
            match="não encontrado ou inativo"
        ):
            criar_reserva(
                id_associado=101,
                id_quiosque=quiosque_teste,
                data_reserva=date.today() + timedelta(days=10)
            )


def test_reserva_cancelada_nao_bloqueia(app, quiosque_teste):
    with app.app_context():
        data_futura = date.today() + timedelta(days=10)

        reserva_cancelada = Reserva(
            id_associado=101,
            id_quiosque=quiosque_teste,
            data_reserva=data_futura,
            status="cancelada"
        )

        db.session.add(reserva_cancelada)
        db.session.commit()

        nova_reserva = criar_reserva(
            id_associado=101,
            id_quiosque=quiosque_teste,
            data_reserva=data_futura
        )

        assert nova_reserva.status == "confirmada"

        quantidade = db.session.query(Reserva).filter_by(
            id_quiosque=quiosque_teste,
            data_reserva=data_futura
        ).count()

        assert quantidade == 2
