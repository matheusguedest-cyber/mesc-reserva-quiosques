
from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    url_for
)

from flask_login import (
    login_user,
    logout_user,
    login_required
)

from app.services.autenticacao import autenticar_associado


# Blueprint responsável pelas rotas de autenticação
autenticacao_bp = Blueprint("autenticacao", __name__)


# Exibe a tela de login no navegador
@autenticacao_bp.route("/login", methods=["GET"])
def exibir_login():
    return render_template("login.html")


# Recebe e valida as credenciais do associado
@autenticacao_bp.route("/login", methods=["POST"])
def login():

    # Identifica se os dados foram enviados em JSON
    if request.is_json:
        dados = request.get_json(silent=True)

        if not isinstance(dados, dict):
            return jsonify({
                "erro": "Envie as credenciais em formato JSON."
            }), 400

        id_associado = dados.get("id_associado")
        senha = dados.get("senha")

    # Recebe os dados enviados pelo formulário HTML
    else:
        id_associado = request.form.get("id_associado")
        senha = request.form.get("senha")

    # Valida a identificação informada
    if (
        not isinstance(id_associado, (str, int))
        or isinstance(id_associado, bool)
        or not str(id_associado).strip()
    ):
        return jsonify({
            "erro": "Informe uma identificação válida."
        }), 400

    # Valida o preenchimento da senha
    if not isinstance(senha, str) or not senha:
        return jsonify({
            "erro": "Informe a senha."
        }), 400

    # Consulta o associado e verifica suas credenciais
    associado = autenticar_associado(id_associado, senha)

    # Trata credenciais inválidas
    if associado is None:

        if request.is_json:
            return jsonify({
                "erro": "Identificação ou senha inválida."
            }), 401

        return render_template(
            "login.html",
            erro="Identificação ou senha inválida."
        ), 401

    # Cria a sessão do associado autenticado
    login_user(associado)

    # Resposta para clientes que utilizam JSON
    if request.is_json:
        return jsonify({
            "mensagem": "Login realizado com sucesso!",
            "associado": {
                "id": associado.id_associado,
                "nome": associado.nome
            }
        }), 200

    # Redireciona o associado após o login pelo navegador
    return redirect(url_for("associados.area_associado"))


# Encerra a sessão do associado

@autenticacao_bp.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    if request.is_json:
        return jsonify({
            "mensagem": "Logout realizado com sucesso!"
        }), 200

    return redirect(url_for("autenticacao.exibir_login"))

