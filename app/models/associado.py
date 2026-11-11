
from datetime import datetime, timezone

from app.extensions import db

from flask_login import UserMixin


class Associado(UserMixin, db.Model):
    __tablename__ = "associados"

    id_associado = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(150),
        nullable=False
    )

    numero_titulo = db.Column(
        db.String(20),
        nullable=False,
        index=True
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=True
    )

    senha_hash = db.Column(
        db.String(255),
        nullable=True
    )

    tipo_vinculo = db.Column(
        db.String(20),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="ativo"
    )

    data_cadastro = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def get_id(self):
        return str(self.id_associado)

    @property
    def is_active(self):
        return self.status == "ativo"


    def __repr__(self):
        return f"<Associado {self.id_associado}: {self.nome}>"
