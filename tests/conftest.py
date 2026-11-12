
from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import Associado
from app.services.autenticacao import gerar_hash_senha


@pytest.fixture
def app(tmp_path, monkeypatch):
    """
    Cria uma aplicação Flask isolada para cada teste,
    utilizando um banco SQLite temporário.
    """

    banco_teste = tmp_path / "mesc_teste.db"

    monkeypatch.setenv(
        "DATABASE_URL",
        f"sqlite:///{banco_teste}"
    )

    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():

        # Cria as tabelas do banco de testes.
        db.create_all()

        # Cadastra um associado para os testes.
        associado = Associado(
            id_associado=101,
            nome="Carlos Silva",
            numero_titulo="1250",
            email=None,
            senha_hash=gerar_hash_senha("Mesc@Teste2026"),
            tipo_vinculo="titular",
            status="ativo"
        )

        db.session.add(associado)
        db.session.commit()

        # Disponibiliza a aplicação para o teste.
        yield app

        # Limpa o banco após a execução.
        db.session.remove()
        db.drop_all()


@pytest.fixture
def cliente(app):
    """
    Cria um cliente HTTP de testes do Flask.
    """
    return app.test_client()


@pytest.fixture
def data_atual_controlada(monkeypatch):
    """
    Simula terça-feira, 17/11/2026,
    para os testes de reservas do MESC.
    """

    import app.services.janela_reservas as janela_reservas
    import app.routes.quiosques as rotas_quiosques

    data_simulada = date(2026, 11, 17)

    # Controla a data utilizada pelo serviço.
    monkeypatch.setattr(
        janela_reservas,
        "obter_data_atual",
        lambda: data_simulada
    )

    # Controla a data utilizada pela rota Flask.
    monkeypatch.setattr(
        rotas_quiosques,
        "obter_data_atual",
        lambda: data_simulada
    )

    return data_simulada
