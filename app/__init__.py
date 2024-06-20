from flask import Flask
from flask_login import LoginManager

from app.models.user import User
from .models import db

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://paci:Gihanga51@localhost/smart_waste_management"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "secret_key"

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

        from .routes.auth import auth_bp
        from .routes.main import main_bp
        from .routes.user import user_bp
        from .routes.services import service_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(user_bp, url_prefix="/user")
        app.register_blueprint(auth_bp, url_prefix="/auth")
        app.register_blueprint(service_bp, url_prefix="/service")

    return app
