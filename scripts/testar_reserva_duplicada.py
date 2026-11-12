
from datetime import date

from sqlalchemy.exc import IntegrityError

from app import create_app
from app.extensions import db
from app.models import Quiosque, Reserva


app = create_app()

with app.app_context():

    quiosque = db.session.query(Quiosque).filter_by(
        numero="01"
    ).first()

    if quiosque is None:
        raise RuntimeError("Quiosque 01 não encontrado.")

    data_teste = date(2026, 11, 20)

    reserva_existente = db.session.query(Reserva).filter_by(
        id_quiosque=quiosque.id_quiosque,
        data_reserva=data_teste,
        status="confirmada"
    ).first()

    if reserva_existente is None:
        raise RuntimeError(
            "A reserva confirmada de teste não foi encontrada."
        )

    print("Reserva original encontrada.")

    reserva_duplicada = Reserva(
        id_associado=101,
        id_quiosque=quiosque.id_quiosque,
        data_reserva=data_teste,
        status="confirmada"
    )

    try:
        db.session.add(reserva_duplicada)
        db.session.flush()

        raise AssertionError(
            "ERRO: o banco permitiu uma reserva duplicada."
        )

    except IntegrityError:
        print("SUCESSO: reserva duplicada bloqueada pelo banco.")

    finally:
        db.session.rollback()

    print("Teste finalizado sem gravar nova reserva.")
