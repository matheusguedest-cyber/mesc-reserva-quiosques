
from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def inicio():
        return "Sistema MESC - Reserva de Quiosques funcionando!"

    return app
