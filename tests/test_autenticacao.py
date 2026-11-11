
import re
from app.extensions import db
from app.models import Associado


def obter_token_csrf(cliente):
    resposta = cliente.get("/login")

    html = resposta.get_data(as_text=True)

    resultado = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        html
    )

    assert resultado is not None

    return resultado.group(1)


def test_login_valido(cliente):

    token = obter_token_csrf(cliente)

    resposta = cliente.post("/login", data={
        "id_associado": "101",
        "senha": "Mesc@Teste2026",
        "csrf_token": token
    })

    assert resposta.status_code == 302
    assert "/area-associado" in resposta.headers["Location"]


def test_login_senha_incorreta(cliente):

    token = obter_token_csrf(cliente)

    resposta = cliente.post("/login", data={
        "id_associado": "101",
        "senha": "SenhaIncorreta123",
        "csrf_token": token
    })

    assert resposta.status_code == 401
    assert b"Identifica" in resposta.data


def test_area_restrita_sem_login(cliente):

    resposta = cliente.get("/area-associado")

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_logout_encerra_sessao(cliente):

    # 1. Obtém o token CSRF do login
    token_login = obter_token_csrf(cliente)

    # 2. Realiza o login
    resposta_login = cliente.post("/login", data={
        "id_associado": "101",
        "senha": "Mesc@Teste2026",
        "csrf_token": token_login
    })

    assert resposta_login.status_code == 302

    # 3. Confirma acesso à área restrita
    resposta_area = cliente.get("/area-associado")

    assert resposta_area.status_code == 200

    # 4. Obtém o token CSRF do formulário de logout
    html_area = resposta_area.get_data(as_text=True)

    resultado = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        html_area
    )

    assert resultado is not None

    token_logout = resultado.group(1)

    # 5. Encerra a sessão
    resposta_logout = cliente.post("/logout", data={
        "csrf_token": token_logout
    })

    assert resposta_logout.status_code == 302
    assert "/login" in resposta_logout.headers["Location"]

    # 6. Tenta acessar novamente a área restrita
    resposta_final = cliente.get("/area-associado")

    assert resposta_final.status_code == 302
    assert "/login" in resposta_final.headers["Location"]


def test_login_sem_token_csrf(cliente):

    resposta = cliente.post("/login", data={
        "id_associado": "101",
        "senha": "Mesc@Teste2026"
    })

    assert resposta.status_code == 400


def test_associado_inativo_nao_pode_login(cliente, app):

    # Altera o associado fictício apenas no banco de teste
    with app.app_context():

        associado = db.session.get(Associado, 101)

        assert associado is not None

        associado.status = "inativo"

        db.session.commit()

    # Obtém o token CSRF do formulário
    token = obter_token_csrf(cliente)

    # Tenta entrar com a senha correta
    resposta = cliente.post("/login", data={
        "id_associado": "101",
        "senha": "Mesc@Teste2026",
        "csrf_token": token
    })

    # O sistema deve negar a autenticação
    assert resposta.status_code == 401

    # Confirma que não foi criada uma sessão autenticada
    with cliente.session_transaction() as sessao:
        assert "_user_id" not in sessao
