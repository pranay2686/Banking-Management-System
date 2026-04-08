import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback_secret_key')

    # Database
    DB_HOST     = os.environ.get('DB_HOST', 'db')
    DB_PORT     = os.environ.get('DB_PORT', '3306')
    DB_NAME     = os.environ.get('DB_NAME', 'bms_db')
    DB_USER     = os.environ.get('DB_USER', 'bms_user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'bms_password123')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail
    MAIL_SERVER         = 'smtp.gmail.com'
    MAIL_PORT           = 587
    MAIL_USE_TLS        = True
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig
}