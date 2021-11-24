from io import  BytesIO
from datetime import datetime

from flask import Blueprint
from flask import abort
from flask import request
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask import flash
from flask import send_from_directory
from flask import current_app

from models import db
from models import User

webui = Blueprint('webui', __name__, static_folder='static', static_url_path='/static/webui', template_folder='templates')





@webui.route("/view/<id>")
def view_screen(id):

    # this is the url for viewing the image
    # only with get request is the image data returned 
    api_url = request.base_url.replace(f"view/{id}",f"v1/live/{id}")
    print (api_url)

    return render_template("index.html", url=api_url)