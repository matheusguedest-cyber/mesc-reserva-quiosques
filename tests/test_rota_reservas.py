
from datetime import date, timedelta

from app.extensions import db
from app.models import Quiosque, Reserva


def preparar_quiosque(app):
    with app.app_context():
        quiosque = Quiosque(
            numero="01",
            capacidade=10,
            status="ativo"
        )

        db.session.add(quiosque)
        db.session.commit()

        return quiosque.id_quiosque


def autenticar_cliente(cliente):
    with cliente.session_transaction() as sessao:
        sessao["_user_id"] = "101"
        sessao["_fresh"] = True


def test_reserva_sem_autenticacao(app, cliente, data_atual_controlada):
    id_quiosque = preparar_quiosque(app)

    resposta = cliente.post(
        "/quiosques/reservar",
        data={
            "id_quiosque": str(id_quiosque),
            "data_reserva": (
                date(2026, 11, 20)
            ).isoformat()
        }
    )

    # O CSRF é validado antes da autenticação.
    assert resposta.status_code == 400


def test_reserva_sem_csrf(app, cliente, data_atual_controlada):
    id_quiosque = preparar_quiosque(app)
    autenticar_cliente(cliente)

    resposta = cliente.post(
        "/quiosques/reservar",
        data={
            "id_quiosque": str(id_quiosque),
            "data_reserva": (
                date(2026, 11, 20)
            ).isoformat()
        }
    )

    assert resposta.status_code == 400


def test_reserva_com_sucesso(app, cliente, data_atual_controlada):
    id_quiosque = preparar_quiosque(app)
    autenticar_cliente(cliente)

    data_futura = date(2026, 11, 20)

    # Acessa a página para obter o token CSRF.
    resposta_get = cliente.get(
        "/quiosques",
        query_string={"data": data_futura.isoformat()}
    )

    assert resposta_get.status_code == 200

    # Extrai o token do formulário HTML.
    from bs4 import BeautifulSoup

    pagina = BeautifulSoup(
        resposta_get.data,
        "html.parser"
    )

    campo_csrf = pagina.find(
        "input",
        {"name": "csrf_token"}
    )

    assert campo_csrf is not None

    resposta_post = cliente.post(
        "/quiosques/reservar",
        data={
            "csrf_token": campo_csrf["value"],
            "id_quiosque": str(id_quiosque),
            "data_reserva": data_futura.isoformat(),

            # Este valor deve ser ignorado pela rota.
            "id_associado": "999"
        },
        follow_redirects=True
    )

    assert resposta_post.status_code == 200
    assert "confirmada com sucesso" in (
        resposta_post.get_data(as_text=True)
    )

    with app.app_context():
        reserva = db.session.query(Reserva).filter_by(
            id_quiosque=id_quiosque,
            data_reserva=data_futura,
            status="confirmada"
        ).first()

        assert reserva is not None

        # A reserva pertence ao usuário autenticado.
        assert reserva.id_associado == 101


def test_reserva_anonima_com_csrf_valido(app, cliente, data_atual_controlada):
    from bs4 import BeautifulSoup

    id_quiosque = preparar_quiosque(app)
    data_futura = date(2026, 11, 20)

    # Obtém um token CSRF válido sem autenticar o usuário.
    resposta_get = cliente.get("/login")
    assert resposta_get.status_code == 200

    pagina = BeautifulSoup(
        resposta_get.data,
        "html.parser"
    )

    campo_csrf = pagina.find(
        "input",
        {"name": "csrf_token"}
    )

    assert campo_csrf is not None

    resposta = cliente.post(
        "/quiosques/reservar",
        data={
            "csrf_token": campo_csrf["value"],
            "id_quiosque": str(id_quiosque),
            "data_reserva": data_futura.isoformat()
        }
    )

    # O Flask-Login redireciona para a página de login.
    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]

    with app.app_context():
        assert db.session.query(Reserva).count() == 0


def test_reserva_duplicada_pela_rota(app, cliente, data_atual_controlada):
    from bs4 import BeautifulSoup

    id_quiosque = preparar_quiosque(app)
    autenticar_cliente(cliente)

    data_futura = date(2026, 11, 20)

    resposta_get = cliente.get(
        "/quiosques",
        query_string={"data": data_futura.isoformat()}
    )

    pagina = BeautifulSoup(
        resposta_get.data,
        "html.parser"
    )

    campo_csrf = pagina.find(
        "input",
        {"name": "csrf_token"}
    )

    assert campo_csrf is not None

    dados = {
        "csrf_token": campo_csrf["value"],
        "id_quiosque": str(id_quiosque),
        "data_reserva": data_futura.isoformat()
    }

    # Primeira solicitação: deve ser confirmada.
    primeira = cliente.post(
        "/quiosques/reservar",
        data=dados,
        follow_redirects=True
    )

    assert primeira.status_code == 200
    assert "confirmada com sucesso" in (
        primeira.get_data(as_text=True)
    )

    # Segunda solicitação: deve ser recusada.
    segunda = cliente.post(
        "/quiosques/reservar",
        data=dados,
        follow_redirects=True
    )

    assert segunda.status_code == 200
    assert "já está reservado" in (
        segunda.get_data(as_text=True)
    )

    with app.app_context():
        quantidade = db.session.query(Reserva).filter_by(
            id_quiosque=id_quiosque,
            data_reserva=data_futura,
            status="confirmada"
        ).count()

        assert quantidade == 1
