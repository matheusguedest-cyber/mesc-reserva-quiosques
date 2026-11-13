
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services import janela_reservas

from app.services.reservas import (
    listar_reservas_associado,
    cancelar_reserva,
    ErroReserva
)


associados_bp = Blueprint("associados", __name__)


@associados_bp.route("/area-associado", methods=["GET"])
@login_required
def area_associado():
    """
    Exibe a área principal do associado autenticado.
    """

    return render_template(
        "area_associado.html",
        associado=current_user
    )


@associados_bp.route("/minhas-reservas", methods=["GET"])
@login_required
def minhas_reservas():
    """
    Exibe as reservas pertencentes ao associado autenticado.
    """

    reservas = listar_reservas_associado(
        current_user.id_associado
    )

    data_atual = janela_reservas.obter_data_atual()

    return render_template(
        "minhas_reservas.html",
        associado=current_user,
        reservas=reservas,
        data_atual=data_atual
    )


@associados_bp.route(
    "/minhas-reservas/<int:id_reserva>/cancelar",
    methods=["POST"]
)
@login_required
def cancelar_reserva_associado(id_reserva):
    """
    Processa o cancelamento de uma reserva
    pertencente ao associado autenticado.
    """

    try:
        cancelar_reserva(
            id_reserva=id_reserva,
            id_associado=current_user.id_associado
        )

        flash(
            "Reserva cancelada com sucesso.",
            "success"
        )

    except ErroReserva as erro:
        flash(str(erro), "danger")

    return redirect(
        url_for("associados.minhas_reservas")
    )
