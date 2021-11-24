from flask import Flask
from api import api
from webui import webui 
from flask_script import Manager
from models import db
from models import User


from config import config


app = Flask(__name__)
app.config.from_object(config['dev'])
app.register_blueprint(api)
app.register_blueprint(webui)
db.init_app(app)


manager = Manager(app)


@manager.command
def initdb():
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    manager.run()
