
from datetime import date

import pytest
from bs4 import BeautifulSoup

from app.extensions import db
from app.models import Quiosque, Reserva


@pytest.fixture
def reserva_teste(app):
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


def autenticar_cliente(cliente):
    with cliente.session_transaction() as sessao:
        sessao["_user_id"] = "101"
        sessao["_fresh"] = True


def obter_token_csrf(cliente):
    resposta = cliente.get("/minhas-reservas")
    assert resposta.status_code == 200

    pagina = BeautifulSoup(
        resposta.data,
        "html.parser"
    )

    campo = pagina.find(
        "input",
        {"name": "csrf_token"}
    )

    assert campo is not None
    return campo["value"]


def test_cancelamento_sem_autenticacao(
    cliente, reserva_teste
):
    resposta = cliente.post(
        f"/minhas-reservas/{reserva_teste}/cancelar"
    )

    # CSRF é validado antes da autenticação.
    assert resposta.status_code == 400


def test_cancelamento_sem_csrf(
    cliente, reserva_teste
):
    autenticar_cliente(cliente)

    resposta = cliente.post(
        f"/minhas-reservas/{reserva_teste}/cancelar"
    )

    assert resposta.status_code == 400


def test_cancelamento_com_sucesso(
    app, cliente, reserva_teste, monkeypatch
):
    monkeypatch.setattr(
        "app.services.janela_reservas.obter_data_atual",
        lambda: date(2026, 11, 19)
    )

    autenticar_cliente(cliente)
    token = obter_token_csrf(cliente)

    resposta = cliente.post(
        f"/minhas-reservas/{reserva_teste}/cancelar",
        data={"csrf_token": token},
        follow_redirects=True
    )

    assert resposta.status_code == 200

    pagina = resposta.get_data(as_text=True)
    assert "Reserva cancelada com sucesso." in pagina

    with app.app_context():
        reserva = db.session.get(Reserva, reserva_teste)
        assert reserva.status == "cancelada"


def test_impedir_cancelamento_de_outro_associado(
    app, cliente, reserva_teste, monkeypatch
):
    monkeypatch.setattr(
        "app.services.janela_reservas.obter_data_atual",
        lambda: date(2026, 11, 19)
    )

    with app.app_context():
        reserva = db.session.get(Reserva, reserva_teste)
        reserva.id_associado = 102

        # Para respeitar a chave estrangeira,
        # criamos o associado proprietário.
        from app.models import Associado

        associado = Associado(
            id_associado=102,
            nome="Maria Oliveira",
            numero_titulo="1250",
            email=None,
            senha_hash="hash_teste",
            tipo_vinculo="dependente",
            status="ativo"
        )

        db.session.add(associado)
        db.session.commit()

    autenticar_cliente(cliente)

    # A reserva do associado 102 não aparece na tela.
    # Obtemos um token válido na área do associado.
    resposta_get = cliente.get("/area-associado")
    pagina = BeautifulSoup(
        resposta_get.data,
        "html.parser"
    )

    token = pagina.find(
        "input",
        {"name": "csrf_token"}
    )["value"]

    resposta = cliente.post(
        f"/minhas-reservas/{reserva_teste}/cancelar",
        data={"csrf_token": token},
        follow_redirects=True
    )

    assert resposta.status_code == 200
    assert "não possui permissão" in (
        resposta.get_data(as_text=True)
    )

    with app.app_context():
        reserva = db.session.get(Reserva, reserva_teste)
        assert reserva.status == "confirmada"


def test_impedir_cancelamento_no_proprio_dia(
    app, cliente, reserva_teste, monkeypatch
):
    monkeypatch.setattr(
        "app.services.janela_reservas.obter_data_atual",
        lambda: date(2026, 11, 20)
    )

    autenticar_cliente(cliente)

    # Obtemos o token em outra página, pois o
    # botão de cancelar não aparece no próprio dia.
    resposta_get = cliente.get("/area-associado")

    pagina = BeautifulSoup(
        resposta_get.data,
        "html.parser"
    )

    token = pagina.find(
        "input",
        {"name": "csrf_token"}
    )["value"]

    resposta = cliente.post(
        f"/minhas-reservas/{reserva_teste}/cancelar",
        data={"csrf_token": token},
        follow_redirects=True
    )

    assert resposta.status_code == 200
    assert "até o dia anterior" in (
        resposta.get_data(as_text=True)
    )

    with app.app_context():
        reserva = db.session.get(Reserva, reserva_teste)
        assert reserva.status == "confirmada"


def test_cancelamento_nao_permite_get(
    cliente, reserva_teste
):
    autenticar_cliente(cliente)

    resposta = cliente.get(
        f"/minhas-reservas/{reserva_teste}/cancelar"
    )

    assert resposta.status_code == 405
