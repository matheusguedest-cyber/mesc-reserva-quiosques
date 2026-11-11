
import pytest

from app import create_app
from app.extensions import db
from app.models import Associado
from app.services.autenticacao import gerar_hash_senha


@pytest.fixture
def app(tmp_path, monkeypatch):

    banco_teste = tmp_path / "mesc_teste.db"

    monkeypatch.setenv(
        "DATABASE_URL",
        f"sqlite:///{banco_teste}"
    )

    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():

        db.create_all()

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

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def cliente(app):
    return app.test_client()
