
from datetime import date

from app.extensions import db
from app.models import Quiosque, Reserva
from app.services.disponibilidade import consultar_disponibilidade


def test_disponibilidade_quiosques(app):

    with app.app_context():

        quiosque_01 = Quiosque(
            numero="01",
            capacidade=10,
            status="ativo"
        )

        quiosque_02 = Quiosque(
            numero="02",
            capacidade=15,
            status="ativo"
        )

        quiosque_03 = Quiosque(
            numero="03",
            capacidade=20,
            status="ativo"
        )

        quiosque_04 = Quiosque(
            numero="04",
            capacidade=10,
            status="inativo"
        )

        db.session.add_all([
            quiosque_01,
            quiosque_02,
            quiosque_03,
            quiosque_04
        ])

        db.session.flush()

        reserva_confirmada = Reserva(
            id_associado=101,
            id_quiosque=quiosque_01.id_quiosque,
            data_reserva=date(2026, 11, 20),
            status="confirmada"
        )

        reserva_cancelada = Reserva(
            id_associado=101,
            id_quiosque=quiosque_02.id_quiosque,
            data_reserva=date(2026, 11, 20),
            status="cancelada"
        )

        db.session.add_all([
            reserva_confirmada,
            reserva_cancelada
        ])

        db.session.commit()

        resultado = consultar_disponibilidade(
            date(2026, 11, 20)
        )

        situacoes = {
            item["numero"]: item["situacao"]
            for item in resultado
        }

        assert situacoes["01"] == "ocupado"
        assert situacoes["02"] == "disponivel"
        assert situacoes["03"] == "disponivel"
        assert situacoes["04"] == "indisponivel"



def test_data_invalida(app, cliente):

    with app.app_context():

        from app.models import Associado
        from flask_login import login_user

        associado = db.session.get(Associado, 101)

        assert associado is not None

    # Simula uma sessão autenticada no cliente de testes.
    with cliente.session_transaction() as sessao:
        sessao["_user_id"] = "101"
        sessao["_fresh"] = True

    resposta = cliente.get(
        "/quiosques?data=2026-02-30"
    )

    assert resposta.status_code == 400

    assert b"Data inv" in resposta.data


def test_acesso_sem_autenticacao(cliente):

    resposta = cliente.get(
        "/quiosques?data=2026-11-20"
    )

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]
