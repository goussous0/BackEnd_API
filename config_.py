from string import ascii_letters, digits
from random import sample
from flask_sqlalchemy import SQLAlchemy
from os import environ

db = SQLAlchemy()


class Config:

    SECRET_KEY = ''.join(sample((ascii_letters + digits), 60))
    uri = os.getenv("DATABASE_URL")
    try:

        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
    except BaseException:
        uri = ''

    SQLALCHEMY_DATABASE_URI = uri or 'sqlite:///data_base.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FILES = '/'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
}
