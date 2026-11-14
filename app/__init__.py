
import os

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from app.extensions import db, login_manager, csrf

from dotenv import load_dotenv

def create_app():
    load_dotenv()

    app = Flask(__name__)


    if os.environ.get("TRUST_PROXY", "false").lower() == "true":
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=1,
            x_proto=1,
            x_host=0,
            x_port=0,
            x_prefix=0
        )

    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    app.config["SESSION_COOKIE_SECURE"] = (
        os.environ.get("SESSION_COOKIE_SECURE", "false").lower()
        == "true"
    )

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

    from app.routes.quiosques import quiosques_bp
    app.register_blueprint(quiosques_bp)

    @app.route("/")
    def inicio():
        return "Sistema MESC - Reserva de Quiosques funcionando!"

    return app

