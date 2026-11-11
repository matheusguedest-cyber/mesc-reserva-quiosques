
from app import create_app

app = create_app()

with app.test_client() as cliente:

    # Teste 1: login com credenciais corretas
    resposta = cliente.post("/login", json={
        "id_associado": 101,
        "senha": "Mesc@Teste2026"
    })

    print("1. Login válido:", resposta.status_code)
    print("   Resposta:", resposta.get_json())

    # Teste 2: verificar se a sessão foi criada
    with cliente.session_transaction() as sessao:
        print("2. Associado na sessão:", sessao.get("_user_id"))

    # Teste 3: encerrar a sessão
    resposta = cliente.post("/logout")

    print("3. Logout:", resposta.status_code)
    print("   Resposta:", resposta.get_json())

    # Teste 4: verificar se a sessão foi encerrada
    with cliente.session_transaction() as sessao:
        print("4. Associado após logout:", sessao.get("_user_id"))

    # Teste 5: login com senha incorreta
    resposta = cliente.post("/login", json={
        "id_associado": 101,
        "senha": "SenhaIncorreta123"
    })

    print("5. Login inválido:", resposta.status_code)
    print("   Resposta:", resposta.get_json())
