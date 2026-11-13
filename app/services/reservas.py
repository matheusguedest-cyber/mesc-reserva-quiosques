
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Associado, Quiosque, Reserva
from app.services.janela_reservas import validar_data_reserva
from app.services import janela_reservas


class ErroReserva(Exception):
    """Representa uma falha nas regras de reserva."""
    pass


def criar_reserva(id_associado, id_quiosque, data_reserva):
    """
    Valida e registra uma reserva de quiosque.

    Retorna a reserva criada ou lança ErroReserva.
    """

    # 1. Validar a data e a janela semanal de reservas
    data_permitida, mensagem_erro = validar_data_reserva(data_reserva)

    if not data_permitida:
        raise ErroReserva(mensagem_erro)

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


def listar_reservas_associado(id_associado):
    """
    Retorna as reservas de um associado.

    Inclui reservas confirmadas e canceladas,
    ordenadas pela data da reserva, da mais
    recente para a mais antiga.
    """

    reservas = (
        db.session.query(Reserva)
        .filter(
            Reserva.id_associado == id_associado
        )
        .order_by(
            Reserva.data_reserva.desc(),
            Reserva.id_reserva.desc()
        )
        .all()
    )

    return reservas


def cancelar_reserva(id_reserva, id_associado):
    """
    Cancela uma reserva pertencente ao associado.

    O cancelamento é permitido somente
    até o dia anterior à data reservada.

    Retorna a reserva atualizada ou
    lança ErroReserva.
    """

    # 1. Localizar a reserva
    reserva = db.session.get(Reserva, id_reserva)

    if reserva is None:
        raise ErroReserva(
            "Reserva não encontrada."
        )

    # 2. Verificar o proprietário
    if reserva.id_associado != id_associado:
        raise ErroReserva(
            "Você não possui permissão para cancelar esta reserva."
        )

    # 3. Verificar o status
    if reserva.status != "confirmada":
        raise ErroReserva(
            "Esta reserva não está confirmada."
        )

    # 4. Validar o prazo de cancelamento
    data_atual = janela_reservas.obter_data_atual()

    if reserva.data_reserva <= data_atual:
        raise ErroReserva(
            "O cancelamento só é permitido até o dia anterior à reserva."
        )

    # 5. Atualizar o status
    reserva.status = "cancelada"

    db.session.commit()

    return reserva
