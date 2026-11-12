
from datetime import date

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

from flask_login import current_user, login_required

from app.services.disponibilidade import consultar_disponibilidade
from app.services.reservas import criar_reserva, ErroReserva

from app.services.janela_reservas import (
    validar_data_reserva,
    obter_janela_atual,
    obter_data_atual
)


quiosques_bp = Blueprint("quiosques", __name__)


@quiosques_bp.route("/quiosques", methods=["GET"])
@login_required
def listar_quiosques():

    # 1. Obter a data atual no fuso horário de São Paulo.
    data_atual = obter_data_atual()

    # 2. Identificar a janela semanal vigente.
    janela = obter_janela_atual(data_atual)

    if janela is None:
        data_minima = None
        data_maxima = None
        periodo_reservas = None

    else:
        inicio, fim = janela

        # Impedir a seleção de datas anteriores à atual.
        primeira_data_permitida = max(data_atual, inicio)

        data_minima = primeira_data_permitida.isoformat()
        data_maxima = fim.isoformat()

        periodo_reservas = (
            f"{primeira_data_permitida:%d/%m/%Y}"
            f" a {fim:%d/%m/%Y}"
        )

    # 3. Obter a data informada pelo associado.
    data_informada = request.args.get("data", "").strip()

    # 4. Exibir a página inicial sem resultados.
    if not data_informada:
        return render_template(
            "quiosques.html",
            data_consulta="",
            quiosques=None,
            erro=None,
            data_minima=data_minima,
            data_maxima=data_maxima,
            periodo_reservas=periodo_reservas
        )

    # 5. Validar o formato da data.
    try:
        data_consulta = date.fromisoformat(data_informada)

    except ValueError:
        return render_template(
            "quiosques.html",
            data_consulta=data_informada,
            quiosques=None,
            erro="Data inválida. Selecione uma data válida.",
            data_minima=data_minima,
            data_maxima=data_maxima,
            periodo_reservas=periodo_reservas
        ), 400

    # 6. Validar a janela semanal de reservas.
    data_permitida, mensagem_erro = validar_data_reserva(
        data_consulta,
        data_atual=data_atual
    )

    if not data_permitida:
        return render_template(
            "quiosques.html",
            data_consulta=data_consulta.isoformat(),
            quiosques=None,
            erro=mensagem_erro,
            data_minima=data_minima,
            data_maxima=data_maxima,
            periodo_reservas=periodo_reservas
        ), 400

    # 7. Consultar a disponibilidade dos quiosques.
    resultado = consultar_disponibilidade(data_consulta)

    # 8. Enviar os resultados para a página HTML.
    return render_template(
        "quiosques.html",
        data_consulta=data_consulta.isoformat(),
        quiosques=resultado,
        erro=None,
        data_minima=data_minima,
        data_maxima=data_maxima,
        periodo_reservas=periodo_reservas
    )


@quiosques_bp.route("/quiosques/reservar", methods=["POST"])
@login_required
def reservar_quiosque():

    # 1. Identificar o associado autenticado.
    id_associado = current_user.id_associado

    # 2. Obter os dados enviados pelo formulário.
    id_quiosque = request.form.get(
        "id_quiosque", ""
    ).strip()

    data_informada = request.form.get(
        "data_reserva", ""
    ).strip()

    # 3. Validar o identificador do quiosque.
    if not id_quiosque.isdigit() or int(id_quiosque) <= 0:
        flash("Quiosque inválido.", "danger")

        return redirect(
            url_for("quiosques.listar_quiosques")
        )

    # 4. Validar o formato da data.
    try:
        data_reserva = date.fromisoformat(data_informada)

    except ValueError:
        flash("Data inválida para reserva.", "danger")

        return redirect(
            url_for("quiosques.listar_quiosques")
        )

    # 5. Executar as regras de negócio.
    # O serviço criar_reserva valida:
    # - Janela semanal de terça-feira a domingo
    # - Datas anteriores à atual
    # - Situação do associado
    # - Situação do quiosque
    # - Existência de reserva confirmada

    try:
        reserva = criar_reserva(
            id_associado=id_associado,
            id_quiosque=int(id_quiosque),
            data_reserva=data_reserva
        )

        flash(
            f"Reserva nº {reserva.id_reserva} "
            "confirmada com sucesso!",
            "success"
        )

    except ErroReserva as erro:
        flash(str(erro), "danger")

    # 6. Retornar à consulta mantendo a data selecionada.
    return redirect(
        url_for(
            "quiosques.listar_quiosques",
            data=data_reserva.isoformat()
        )
    )
