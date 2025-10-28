"""Flask App configuration."""
from os import environ, path
import os
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))

# Loging
load_dotenv(path.join(basedir, ".env"))

LOG_LEVEL = environ.get('LOG_LEVEL', 'DEBUG').upper()
SALT = environ.get('SALT')

# General Config
ENVIRONMENT = "development"
FLASK_APP = "app.py"
FLASK_DEBUG = True
SECRET_KEY = environ.get("SECRET_KEY", "dev-secret-key")
DEBUG_TB_ENABLED = True
DEBUG_TB_INTERCEPT_REDIRECTS = False

# Mail config
MAIL_SENDER_ADDR= environ.get("MAIL_SENDER_ADDR")
MAIL_SENDER_PASSWORD=environ.get("MAIL_SENDER_PASSWORD")
MAIL_SMTP_SERVER=environ.get("MAIL_SMTP_SERVER")
MAIL_SMTP_PORT=environ.get("MAIL_SMTP_PORT")
CONTACT_ADDR=environ.get("CONTACT_ADDR")


UPLOAD_FOLDER = os.path.join(basedir, 'wannapop/static/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.dirname(__file__), "sqlite", "database.db")      
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True
SQLALCHEMY_RECORD_QUERIES = True


