
from datetime import date

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Associado, Quiosque, Reserva


class ErroReserva(Exception):
    """Representa uma falha nas regras de reserva."""
    pass


def criar_reserva(id_associado, id_quiosque, data_reserva):
    """
    Valida e registra uma reserva de quiosque.

    Retorna a reserva criada ou lança ErroReserva.
    """

    # 1. Validar a data informada
    if not isinstance(data_reserva, date) or isinstance(
        data_reserva, __import__("datetime").datetime
    ):
        raise ErroReserva("A data informada é inválida.")

    if data_reserva < date.today():
        raise ErroReserva(
            "Não é permitido reservar datas anteriores à data atual."
        )

    # 2. Validar o associado
    associado = db.session.get(Associado, id_associado)

    if associado is None or not associado.is_active:
        raise ErroReserva(
            "Associado não encontrado ou inativo."
        )

    # 3. Validar o quiosque
    quiosque = db.session.get(Quiosque, id_quiosque)

    if quiosque is None:
        raise ErroReserva("Quiosque não encontrado.")

    if quiosque.status != "ativo":
        raise ErroReserva(
            "Este quiosque não está disponível para reservas."
        )

    # 4. Verificar se já existe reserva confirmada
    reserva_existente = db.session.query(Reserva).filter_by(
        id_quiosque=id_quiosque,
        data_reserva=data_reserva,
        status="confirmada"
    ).first()

    if reserva_existente is not None:
        raise ErroReserva(
            "Este quiosque já está reservado para a data selecionada."
        )

    # 5. Criar a reserva
    nova_reserva = Reserva(
        id_associado=id_associado,
        id_quiosque=id_quiosque,
        data_reserva=data_reserva,
        status="confirmada"
    )

    try:
        db.session.add(nova_reserva)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        raise ErroReserva(
            "Este quiosque já foi reservado por outro associado."
        ) from None

    return nova_reserva
