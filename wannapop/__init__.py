import os
import logging
from logging.handlers import RotatingFileHandler
from .hashid_utils import encode_id, decode_id
from .helper_mail import MailManager
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_principal import Principal
from flask_wtf.csrf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension
from config import LOG_LEVEL
from types import SimpleNamespace  


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
principal_manager = Principal()
mail_manager = MailManager()
csrf = CSRFProtect()
toolbar = DebugToolbarExtension()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    @app.context_processor
    def utility_processor():

        return dict(
            encode_id=encode_id,
            decode_id=decode_id,
            hashids=SimpleNamespace(encode=encode_id)  
        )

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    principal_manager.init_app(app)
    mail_manager.init_app(app)
    csrf.init_app(app)
    toolbar.init_app(app)


    register_blueprints(app)

    setup_login_manager()

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()


    setup_logging(app)

    app.logger.info("Aplicacion iniciada")
    return app


def register_blueprints(app):
    """ Registrar todos los blueprints."""
    from .routes_main import main_page
    from .routers_users import routers_user
    from .routes_products import routes_products
    from .routers_auth import auth_page
    from .routers_block_users import routers_block_users
    from .routes_block_products import routes_block_products
    from .routes_profile import routes_profile
    from .routes_admin import routes_admin
    from .routers_sales import routes_sales
    from .routes_purchases import routes_purchases

    app.register_blueprint(main_page)
    app.register_blueprint(routers_user)
    app.register_blueprint(routes_products)
    app.register_blueprint(auth_page)
    app.register_blueprint(routers_block_users)
    app.register_blueprint(routes_block_products)
    app.register_blueprint(routes_profile)
    
    app.register_blueprint(routes_admin)
    app.register_blueprint(routes_sales)
    app.register_blueprint(routes_purchases)

def setup_login_manager():
    """Config login_manager y cargar el usuario."""
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = "auth_page.login"
    login_manager.login_message = "Por favor, inicia sesion para acceder a esta pagina."
    login_manager.login_message_category = "warning"


def setup_logging(app):
    """Config logging."""
    log_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=3)
    log_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    log_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(log_handler)

    if LOG_LEVEL not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        raise ValueError('Nivell de registre no vàlid')

    app.logger.setLevel(getattr(logging, LOG_LEVEL))
