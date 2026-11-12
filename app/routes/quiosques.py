
from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.services.disponibilidade import consultar_disponibilidade
from app.services.reservas import criar_reserva, ErroReserva

quiosques_bp = Blueprint("quiosques", __name__)

@quiosques_bp.route("/quiosques", methods=["GET"])
@login_required
def listar_quiosques():

    data_informada = request.args.get("data", "").strip()

    # A página inicial aparece sem resultados.
    if not data_informada:
        return render_template(
            "quiosques.html",
            data_consulta="",
            quiosques=None,
            erro=None
        )

    # Valida a data recebida do formulário.
    try:
        data_consulta = date.fromisoformat(data_informada)

    except ValueError:
        return render_template(
            "quiosques.html",
            data_consulta=data_informada,
            quiosques=None,
            erro="Data inválida. Selecione uma data válida."
        ), 400

    # Consulta a disponibilidade no serviço.
    resultado = consultar_disponibilidade(data_consulta)

    # Envia os resultados para a página HTML.
    return render_template(
        "quiosques.html",
        data_consulta=data_consulta.isoformat(),
        quiosques=resultado,
        erro=None
    )


@quiosques_bp.route("/quiosques/reservar", methods=["POST"])
@login_required
def reservar_quiosque():

    # Identifica o associado pela sessão autenticada.
    id_associado = current_user.id_associado

    # Obtém os dados enviados pelo formulário.
    id_quiosque = request.form.get("id_quiosque", "").strip()
    data_informada = request.form.get("data_reserva", "").strip()

    # Valida o identificador do quiosque.
    if not id_quiosque.isdigit() or int(id_quiosque) <= 0:
        flash("Quiosque inválido.", "danger")
        return redirect(url_for("quiosques.listar_quiosques"))

    # Valida a data.
    try:
        data_reserva = date.fromisoformat(data_informada)

    except ValueError:
        flash("Data inválida para reserva.", "danger")
        return redirect(url_for("quiosques.listar_quiosques"))

    # Executa as regras de negócio do serviço.
    try:
        reserva = criar_reserva(
            id_associado=id_associado,
            id_quiosque=int(id_quiosque),
            data_reserva=data_reserva
        )

        flash(
            f"Reserva nº {reserva.id_reserva} confirmada com sucesso!",
            "success"
        )

    except ErroReserva as erro:
        flash(str(erro), "danger")

    # Retorna à consulta mantendo a data selecionada.
    return redirect(
        url_for(
            "quiosques.listar_quiosques",
            data=data_reserva.isoformat()
        )
    )
