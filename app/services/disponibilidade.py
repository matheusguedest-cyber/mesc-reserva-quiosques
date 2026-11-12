
from datetime import date

from app.extensions import db
from app.models import Quiosque, Reserva


def consultar_disponibilidade(data_consulta):

    # Valida o tipo da data recebida
    if not isinstance(data_consulta, date):
        raise ValueError(
            "A data informada deve ser uma data válida."
        )

    # Consulta as reservas confirmadas para a data
    reservas_confirmadas = db.session.query(
        Reserva.id_quiosque
    ).filter(
        Reserva.data_reserva == data_consulta,
        Reserva.status == "confirmada"
    ).all()

    # Cria um conjunto com os IDs dos quiosques ocupados
    quiosques_ocupados = {
        id_quiosque
        for (id_quiosque,) in reservas_confirmadas
    }

    # Consulta todos os quiosques cadastrados
    quiosques = db.session.query(
        Quiosque
    ).order_by(
        Quiosque.numero
    ).all()

    resultado = []

    for quiosque in quiosques:

        if quiosque.status != "ativo":
            situacao = "indisponivel"

        elif quiosque.id_quiosque in quiosques_ocupados:
            situacao = "ocupado"

        else:
            situacao = "disponivel"

        resultado.append({
            "id_quiosque": quiosque.id_quiosque,
            "numero": quiosque.numero,
            "capacidade": quiosque.capacidade,
            "descricao": quiosque.descricao,
            "situacao": situacao
        })

    return resultado
