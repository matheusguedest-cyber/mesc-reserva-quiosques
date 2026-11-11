
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


def gerar_hash_senha(senha):
    """Gera um hash seguro para armazenar a senha."""

    if not isinstance(senha, str) or len(senha) < 12:
        raise ValueError(
            "A senha deve possuir pelo menos 12 caracteres."
        )

    return generate_password_hash(
        senha,
        method="scrypt"
    )


def verificar_senha(senha_hash, senha):
    """Verifica se a senha informada corresponde ao hash."""

    if not senha_hash or not isinstance(senha, str):
        return False

    return check_password_hash(
        senha_hash,
        senha
    )


def autenticar_associado(id_associado, senha):
    """Autentica um associado pelo ID individual e senha."""

    from app.extensions import db
    from app.models import Associado

    try:
        id_associado = int(id_associado)
    except (TypeError, ValueError):
        return None

    associado = db.session.get(Associado, id_associado)

    if associado is None:
        return None

    if associado.status != "ativo":
        return None

    if not verificar_senha(associado.senha_hash, senha):
        return None

    return associado
