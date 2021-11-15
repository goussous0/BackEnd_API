from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    pass_hash = db.Column(db.String(1000))
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(150))

    # this indicates if user is currently active
    # changes to false if user does not use token in 1 min
    is_active = db.Column(db.Boolean(), nullable=False, default=False)

    last_login = db.Column(db.DateTime())

    is_superuser = db.Column(db.Boolean(), default=False)
