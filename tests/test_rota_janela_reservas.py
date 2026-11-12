
from datetime import date

from app.extensions import db
from app.models import Quiosque


def autenticar_cliente(cliente):
    with cliente.session_transaction() as sessao:
        sessao["_user_id"] = "101"
        sessao["_fresh"] = True


def preparar_quiosque(app):
    with app.app_context():
        quiosque = Quiosque(
            numero="01",
            capacidade=10,
            status="ativo"
        )

        db.session.add(quiosque)
        db.session.commit()


def test_consulta_data_permitida(
    app, cliente, data_atual_controlada
):
    preparar_quiosque(app)
    autenticar_cliente(cliente)

    resposta = cliente.get(
        "/quiosques",
        query_string={"data": "2026-11-20"}
    )

    pagina = resposta.get_data(as_text=True)

    assert resposta.status_code == 200
    assert "Reservar quiosque" in pagina


def test_consulta_fora_da_janela(
    app, cliente, data_atual_controlada
):
    preparar_quiosque(app)
    autenticar_cliente(cliente)

    resposta = cliente.get(
        "/quiosques",
        query_string={"data": "2026-11-23"}
    )

    pagina = resposta.get_data(as_text=True)

    assert resposta.status_code == 400
    assert "fora da janela" in pagina
    assert "Reservar quiosque" not in pagina


def test_consulta_data_passada(
    app, cliente, data_atual_controlada
):
    preparar_quiosque(app)
    autenticar_cliente(cliente)

    resposta = cliente.get(
        "/quiosques",
        query_string={"data": "2026-11-16"}
    )

    pagina = resposta.get_data(as_text=True)

    assert resposta.status_code == 400
    assert "datas anteriores" in pagina
    assert "Reservar quiosque" not in pagina



def test_consulta_segunda_feira_fechada(
    app, cliente, monkeypatch
):
    import app.services.janela_reservas as janela
    import app.routes.quiosques as rotas_quiosques

    # Simula segunda-feira, 16/11/2026.
    data_simulada = date(2026, 11, 16)

    # Atualiza a data utilizada pelo serviço.
    monkeypatch.setattr(
        janela,
        "obter_data_atual",
        lambda: data_simulada
    )

    # Atualiza a data utilizada pela rota Flask.
    monkeypatch.setattr(
        rotas_quiosques,
        "obter_data_atual",
        lambda: data_simulada
    )

    preparar_quiosque(app)
    autenticar_cliente(cliente)

    resposta = cliente.get(
        "/quiosques",
        query_string={"data": "2026-11-20"}
    )

    pagina = resposta.get_data(as_text=True)

    assert resposta.status_code == 400
    assert "reservas estão fechadas" in pagina
    assert "Reservar" not in pagina
