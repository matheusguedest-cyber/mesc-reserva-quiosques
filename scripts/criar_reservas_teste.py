
from datetime import date

from app import create_app
from app.extensions import db
from app.models import Quiosque, Reserva


app = create_app()

data_teste = date(2026, 11, 20)

reservas_teste = [
    {
        "numero_quiosque": "01",
        "status": "confirmada"
    },
    {
        "numero_quiosque": "02",
        "status": "cancelada"
    }
]


with app.app_context():

    for dados in reservas_teste:

        quiosque = db.session.query(Quiosque).filter_by(
            numero=dados["numero_quiosque"]
        ).first()

        if quiosque is None:
            print("Quiosque não encontrado.")
            continue

        reserva_existente = db.session.query(Reserva).filter_by(
            id_quiosque=quiosque.id_quiosque,
            data_reserva=data_teste,
            status=dados["status"]
        ).first()

        if reserva_existente:
            print(
                f"Reserva do quiosque {quiosque.numero} "
                "já cadastrada."
            )
            continue

        reserva = Reserva(
            id_associado=101,
            id_quiosque=quiosque.id_quiosque,
            data_reserva=data_teste,
            status=dados["status"]
        )

        db.session.add(reserva)

        print(
            f"Reserva {dados['status']} criada "
            f"para o quiosque {quiosque.numero}."
        )

    db.session.commit()

    print("Processamento concluído.")
