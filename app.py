from flask import Flask ,render_template,request ,url_for ,redirect ,send_from_directory
from api import api 
from flask_script import Manager
#from flask_security import current_user


import os 

from models import db 
from models import User


from config import config



app = Flask(__name__)
app.config.from_object(config['dev'])
app.register_blueprint(api)
db.init_app(app)


manager = Manager(app)




@manager.command
def initdb():
    db.drop_all()
    db.create_all()
    db.session.commit()

    
if __name__ == '__main__':
    manager.run()