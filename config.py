from string import ascii_letters, digits
from random import sample


class Config:
    SECRET_KEY = ''.join(sample((ascii_letters + digits), 60))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig
}
