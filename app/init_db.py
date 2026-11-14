
from app import create_app
from app.extensions import db
from app.models import Associado, Quiosque, Reserva


def inicializar_banco():
    app = create_app()

    with app.app_context():
        tipo_banco = db.engine.dialect.name

        print(f"Banco identificado: {tipo_banco}")

        if tipo_banco != "postgresql":
            raise RuntimeError(
                "Inicialização interrompida: "
                "este comando exige PostgreSQL."
            )

        db.create_all()

        print("Tabelas verificadas e criadas, se necessário.")


if __name__ == "__main__":
    inicializar_banco()
