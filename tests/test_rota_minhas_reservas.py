
from datetime import date

from app.extensions import db
from app.models import Associado, Quiosque, Reserva


def autenticar_cliente(cliente):
    """
    Simula a autenticação do associado 101.
    """
    with cliente.session_transaction() as sessao:
        sessao["_user_id"] = "101"
        sessao["_fresh"] = True


def preparar_reservas():
    """
    Cria reservas para dois associados que
    compartilham o mesmo título familiar.
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


def test_minhas_reservas_sem_autenticacao(cliente):
    """
    Visitantes não autenticados devem
    ser redirecionados para o login.
    """

    resposta = cliente.get("/minhas-reservas")

    assert resposta.status_code == 302

    assert "/login" in resposta.headers["Location"]


def test_minhas_reservas_associado_autenticado(app, cliente):
    """
    O associado deve conseguir consultar
    suas reservas confirmadas.
    """

    with app.app_context():
        preparar_reservas()

    autenticar_cliente(cliente)

    resposta = cliente.get("/minhas-reservas")

    assert resposta.status_code == 200

    pagina = resposta.get_data(as_text=True)

    assert "Minhas Reservas" in pagina
    assert "Quiosque 01" in pagina
    assert "20/11/2026" in pagina
    assert "Confirmada" in pagina


def test_minhas_reservas_nao_exibe_outro_associado(app, cliente):
    """
    Um associado não deve visualizar
    reservas pertencentes a outro.
    """

    with app.app_context():
        preparar_reservas()

    autenticar_cliente(cliente)

    resposta = cliente.get("/minhas-reservas")

    assert resposta.status_code == 200

    pagina = resposta.get_data(as_text=True)

    # Reserva pertencente ao associado 101.
    assert "Quiosque 01" in pagina

    # Reserva pertencente ao associado 102.
    assert "Quiosque 02" not in pagina
    assert "21/11/2026" not in pagina
