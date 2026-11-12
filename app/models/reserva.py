
from datetime import datetime, timezone

from app.extensions import db


class Reserva(db.Model):

    __tablename__ = "reservas"

    __table_args__ = (
        db.Index(
            "uq_reserva_confirmada_quiosque_data",
            "id_quiosque",
            "data_reserva",
            unique=True,
            sqlite_where=db.text("status = 'confirmada'"),
            postgresql_where=db.text("status = 'confirmada'")
        ),
    )


    id_reserva = db.Column(
        db.Integer,
        primary_key=True
    )

    id_associado = db.Column(
        db.Integer,
        db.ForeignKey("associados.id_associado"),
        nullable=False
    )

    id_quiosque = db.Column(
        db.Integer,
        db.ForeignKey("quiosques.id_quiosque"),
        nullable=False
    )

    data_reserva = db.Column(
        db.Date,
        nullable=False,
        index=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="confirmada"
    )

    data_criacao = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    associado = db.relationship(
        "Associado",
        backref="reservas"
    )

    quiosque = db.relationship(
        "Quiosque",
        backref="reservas"
    )

    def __repr__(self):
        return (
            f"<Reserva {self.id_reserva} - "
            f"Quiosque {self.id_quiosque}>"
        )
