# app/__init__.py

from flask import Flask
from flask_login import LoginManager
from app.models import db
from app.models.user import User
from dotenv import load_dotenv
import os

login_manager = LoginManager()


def create_app(config_name=None, config_obj=None):
    app = Flask(__name__)

    # Load environment variables from .env file
    load_dotenv()

    if config_name == "testing":
        app.config.from_object(config_obj)
    else:
        # Load configuration from environment variables
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = (
            os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS") == "True"
        )
        app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

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
        from .routes.admin import admin_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(user_bp, url_prefix="/user")
        app.register_blueprint(auth_bp, url_prefix="/auth")
        app.register_blueprint(service_bp, url_prefix="/service")
        app.register_blueprint(admin_bp, url_prefix="/admin")

    return app
