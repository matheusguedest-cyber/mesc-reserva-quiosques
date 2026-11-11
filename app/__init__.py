
import os

from flask import Flask

from app.extensions import db, login_manager, csrf

from dotenv import load_dotenv

def create_app():
    load_dotenv()

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "sqlite:///mesc_dev.db"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    from app.models import Associado
    
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "autenticacao.exibir_login"

    @login_manager.user_loader
    def carregar_associado(id_associado):
        try:
            return db.session.get(Associado, int(id_associado))
        except (ValueError, TypeError):
            return None


    from app.routes.autenticacao import autenticacao_bp
    app.register_blueprint(autenticacao_bp)

    from app.routes.associados import associados_bp
    app.register_blueprint(associados_bp)

    @app.route("/")
    def inicio():
        return "Sistema MESC - Reserva de Quiosques funcionando!"

    return app

