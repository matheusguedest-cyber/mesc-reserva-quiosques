
import os
from getpass import getpass

from app import create_app
from app.extensions import db
from app.models import Associado, Quiosque
from app.services.autenticacao import gerar_hash_senha


def popular_homologacao():
    app = create_app()

    with app.app_context():
        if db.engine.dialect.name != "postgresql":
            raise RuntimeError(
                "Este script exige PostgreSQL."
            )

        if os.environ.get("CONFIRMAR_HOMOLOGACAO") != "SIM":
            raise RuntimeError(
                "Defina CONFIRMAR_HOMOLOGACAO=SIM "
                "para autorizar o cadastro."
            )

        id_teste = 900001

        associado = db.session.get(Associado, id_teste)

        if associado is not None:
            raise RuntimeError(
                "O ID 900001 já existe. "
                "Nenhum registro será inserido."
            )

        numeros = ("01", "02", "03")

        existentes = Quiosque.query.filter(
            Quiosque.numero.in_(numeros)
        ).first()

        if existentes is not None:
            raise RuntimeError(
                "Já existe um dos quiosques de teste. "
                "Nenhum registro será inserido."
            )

        senha = getpass(
            "Defina a senha do associado fictício: "
        )

        senha_hash = gerar_hash_senha(senha)

        associado = Associado(
            id_associado=id_teste,
            nome="Associado Teste MESC",
            numero_titulo="TESTE001",
            email=None,
            senha_hash=senha_hash,
            tipo_vinculo="titular",
            status="ativo"
        )

        quiosques = [
            Quiosque(
                numero="01",
                capacidade=10,
                descricao="Quiosque fictício 01",
                status="ativo"
            ),
            Quiosque(
                numero="02",
                capacidade=15,
                descricao="Quiosque fictício 02",
                status="ativo"
            ),
            Quiosque(
                numero="03",
                capacidade=20,
                descricao="Quiosque fictício 03",
                status="ativo"
            )
        ]

        try:
            db.session.add(associado)
            db.session.add_all(quiosques)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        print("Dados fictícios cadastrados com sucesso.")
        print("ID de login: 900001")
        print("Quiosques cadastrados: 01, 02 e 03")


if __name__ == "__main__":
    popular_homologacao()
