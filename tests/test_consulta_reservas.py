
from datetime import date

from app.extensions import db
from app.models import Associado, Quiosque, Reserva
from app.services.reservas import listar_reservas_associado


def preparar_dados_teste():
    """
    Cria dois associados, dois quiosques
    e reservas para testar a consulta.
    """

    associado_2 = Associado(
        id_associado=102,
        nome="Maria Oliveira",
        numero_titulo="1250",
        email=None,
        senha_hash="hash_teste",
        tipo_vinculo="dependente",
        status="ativo"
    )

    quiosque_1 = Quiosque(
        numero="01",
        capacidade=10,
        status="ativo"
    )

    quiosque_2 = Quiosque(
        numero="02",
        capacidade=15,
        status="ativo"
    )

    db.session.add_all([
        associado_2,
        quiosque_1,
        quiosque_2
    ])

    db.session.flush()

    reserva_1 = Reserva(
        id_associado=101,
        id_quiosque=quiosque_1.id_quiosque,
        data_reserva=date(2026, 11, 20),
        status="confirmada"
    )

    reserva_2 = Reserva(
        id_associado=102,
        id_quiosque=quiosque_2.id_quiosque,
        data_reserva=date(2026, 11, 21),
        status="confirmada"
    )

    db.session.add_all([
        reserva_1,
        reserva_2
    ])

    db.session.commit()

    return reserva_1.id_reserva, reserva_2.id_reserva


def test_consultar_reservas_do_associado(app):
    """
    Verifica se o associado consegue
    consultar suas próprias reservas.
    """

    with app.app_context():

        id_reserva_1, _ = preparar_dados_teste()

        reservas = listar_reservas_associado(101)

        assert len(reservas) == 1
        assert reservas[0].id_reserva == id_reserva_1
        assert reservas[0].id_associado == 101
        assert reservas[0].status == "confirmada"


def test_nao_retornar_reservas_de_outro_associado(app):
    """
    Verifica o isolamento das reservas
    entre associados diferentes.
    """

    with app.app_context():

        _, id_reserva_2 = preparar_dados_teste()

        reservas = listar_reservas_associado(101)

        ids_reservas = [
            reserva.id_reserva
            for reserva in reservas
        ]

        assert id_reserva_2 not in ids_reservas

        assert all(
            reserva.id_associado == 101
            for reserva in reservas
        )


def test_consulta_inclui_reservas_canceladas(app):
    """
    Verifica se reservas canceladas
    permanecem no histórico.
    """

    with app.app_context():

        id_reserva_1, _ = preparar_dados_teste()

        reserva = db.session.get(
            Reserva,
            id_reserva_1
        )

        reserva.status = "cancelada"
        db.session.commit()

        reservas = listar_reservas_associado(101)

        assert len(reservas) == 1
        assert reservas[0].id_reserva == id_reserva_1
        assert reservas[0].status == "cancelada"
