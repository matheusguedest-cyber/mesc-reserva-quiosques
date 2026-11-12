
from sqlalchemy import inspect, text

from app import create_app
from app.extensions import db
from app.models import Reserva


NOME_INDICE = "uq_reserva_confirmada_quiosque_data"


def atualizar_indice():
    app = create_app()

    with app.app_context():
        # Confirma que a tabela já existe.
        inspetor = inspect(db.engine)

        if not inspetor.has_table("reservas"):
            raise RuntimeError(
                "A tabela reservas não existe. "
                "Inicialize o banco antes de executar a atualização."
            )

        # Verifica duplicidades antes de criar o índice.
        consulta = text("""
            SELECT id_quiosque, data_reserva, COUNT(*) AS quantidade
            FROM reservas
            WHERE status = 'confirmada'
            GROUP BY id_quiosque, data_reserva
            HAVING COUNT(*) > 1
        """)

        with db.engine.connect() as conexao:
            duplicidades = conexao.execute(consulta).all()

        if duplicidades:
            print("Foram encontradas reservas duplicadas:")

            for registro in duplicidades:
                print(registro)

            raise RuntimeError(
                "Corrija as duplicidades antes de criar o índice."
            )

        # Procura o índice no modelo SQLAlchemy.
        indice = next(
            indice
            for indice in Reserva.__table__.indexes
            if indice.name == NOME_INDICE
        )

        # Cria o índice apenas se ele ainda não existir.
        indice.create(
            bind=db.engine,
            checkfirst=True
        )

        # Confirma que o índice foi criado.
        indices = inspect(db.engine).get_indexes("reservas")

        indice_criado = next(
            (item for item in indices if item["name"] == NOME_INDICE),
            None
        )

        if indice_criado is None or not indice_criado["unique"]:
            raise RuntimeError(
                "Não foi possível confirmar o índice único."
            )

        print("Índice único de reservas verificado com sucesso.")


if __name__ == "__main__":
    atualizar_indice()
