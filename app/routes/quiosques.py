
from datetime import date

from flask import Blueprint, render_template, request
from flask_login import login_required

from app.services.disponibilidade import consultar_disponibilidade

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