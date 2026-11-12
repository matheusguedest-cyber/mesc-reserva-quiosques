
from app.extensions import db


class Quiosque(db.Model):

    __tablename__ = "quiosques"

    id_quiosque = db.Column(
        db.Integer,
        primary_key=True
    )

    numero = db.Column(
        db.String(10),
        nullable=False,
        unique=True
    )

    capacidade = db.Column(
        db.Integer,
        nullable=False
    )

    descricao = db.Column(
        db.String(200),
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="ativo"
    )

    def __repr__(self):
        return f"<Quiosque {self.numero}>"
