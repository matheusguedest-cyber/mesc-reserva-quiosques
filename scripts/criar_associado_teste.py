
from app import create_app
from app.extensions import db
from app.models import Associado
from app.services.autenticacao import gerar_hash_senha


app = create_app()

with app.app_context():

    associado = db.session.get(Associado, 101)

    if associado is None:

        associado = Associado(
            id_associado=101,
            nome="Carlos Silva",
            numero_titulo="1250",
            email=None,
            senha_hash=gerar_hash_senha("Mesc@Teste2026"),
            tipo_vinculo="titular",
            status="ativo"
        )

        db.session.add(associado)
        db.session.commit()

        print("Associado fictício cadastrado com sucesso!")

    else:
        print("Associado fictício já está cadastrado.")

    print("ID:", associado.id_associado)
    print("Nome:", associado.nome)
    print("Título:", associado.numero_titulo)
    print("E-mail:", associado.email)
    print("Status:", associado.status)
    print(
        "Senha armazenada com scrypt:",
        associado.senha_hash.startswith("scrypt:")
    )
