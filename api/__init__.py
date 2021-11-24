from base64 import b64decode
from flask import jsonify, request, Blueprint, session
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

from functools import wraps
from datetime import datetime, timedelta
from config import config
import jwt
from models import db
from models import User

from sqlalchemy import exc


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = (request.headers['x-access-tokens']).encode("UTF-8")
        if not token:
            return jsonify({"API_return_code": "Unauthorized"}), 401
        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithm='HS256')

            # check request id against token id
            # print (f"UserID in Request = {request.url[-1]}" )
            # print (f"UserID in Token   = {data['user_id']}")
            # when UserID in token does not match that of  request means
            # a user or attacker is using a token of another user to look info
            # as authorized user of the token ID
            if str(request.url[-1]) != str(data['user_id']):
                return jsonify({"API_return_code": "Unauthorized"}), 401

            else:
                return f(*args, **kwargs)

        except BaseException:
            return jsonify({"API_return_code": "Unauthorized"}), 401

    return decorator


api = Blueprint('api', __name__, url_prefix="/v1")


# API routes
@api.route('/api-token-auth', methods=['POST'])
def token_auth():
    # takes two arguments a username and a password as a json
    """
    {
        "username": "string",
        "password": "string"
    }
    """

    if not request.json:
        return jsonify({"API_return_code": "No json provided"}), 400

    if request.method == 'POST':

        tmp_user = User.query.filter_by(
            username=request.json['username']).first()
        if not tmp_user:
            return jsonify({"API_return_code": "No such user"}), 404

        # validate user and check provided password
        if check_password_hash(tmp_user.pass_hash, request.json['password']):
            # the user name and password provided are valid
            # generate token

            # make sure user is active
            tmp_user.is_active = True
            tmp_user.last_login = datetime.now()
            db.session.commit()

            token = jwt.encode({'user_id': tmp_user.id,
                                'exp': datetime.utcnow() + timedelta(hours=1)},
                               current_app.config['SECRET_KEY'],
                               algorithm='HS256')

            return jsonify(
                {"API_return_code": "Successfully authenticated user",
                 "UserID": tmp_user.id,
                 "token": token.decode('UTF-8')}), 200
        else:
            return jsonify(
                {"API_return_code": "Forbidden wrong password "}), 403

    else:
        return jsonify({"API_return_code": "Wrong request method"}), 400


# GET request returns all users POST creates new user

@api.route('/users', methods=['GET', 'POST'])
# @token_required
def users():

    all_users = User.query.all()

    # if get then we return the users
    if request.method == "GET":
        users_lst = []

        for user in all_users:
            user.is_online()
            # username, first_name, last_name, last_login, is_active
            sub_lst = [user.id,
                       user.username,
                       user.first_name,
                       user.last_name,
                       user.is_active]
            users_lst.append(sub_lst)

        return jsonify({"API_return_code": "Returned Users list",
                       "Users_list": users_lst}), 200

    # create new user if json data found
    elif request.method == "POST":
        # sample data for valid POST request
        """
                {
                "username": "hello",
                "first_name": "hello",
                "last_name": "world",
                "password": "1234",
                }
        """

        if not request.json:
            return jsonify({"API_return_code": "No JSON"}), 401

        json_data = request.json

        for item in json_data:
            if json_data[item] == "":
                return jsonify(
                    {"API_return_code": "Can't have empty values"}), 401

        try:
            new_user = User(
                username=json_data['username'],
                pass_hash=generate_password_hash(
                    json_data['password'],
                    "sha256"),
                first_name=json_data['first_name'],
                last_name=json_data['last_name'],
                last_login=datetime.now(),
                is_active=True)
            db.session.add(new_user)
            db.session.commit()

        except exc.IntegrityError as IE:
            db.session.rollback()
            return jsonify(
                {"API_return_code": "Such username is already registered."})

        return jsonify({"API_return_code": "Added New User.",
                       "UserID": f"{new_user.id}"}), 200


# read user
@api.route('/users/<id>', methods=['GET'])
@token_required
def read_user(id):

    user_by_id = User.query.filter_by(id=id).first()

    # convert user info into dictionary
    this_user = {"username": user_by_id.username,
                 "first_name": user_by_id.first_name,
                 "last_name": user_by_id.last_name,
                 "last_login": str(user_by_id.last_login),
                 "is_active": user_by_id.is_active,
                 "is_super": user_by_id.is_super}

    return jsonify({"API_return_code": "User Found",
                   "UserInfo": this_user}), 200


# update user info
@api.route('/users/<id>', methods=['PUT'])
# @token_required
def update_user(id):
    # updates every property of the user object to the value in json
    # json must have all the values

    # grab the user with specified id
    this_user = User.query.filter_by(id=id).first()
    if not this_user:
        return jsonify({"API_return_code": "No such user"}), 404

    """
    {
        "username": "string",
        "first_name": "string",
        "last_name": "string"
    }
    """

    if request.method == "PUT":
        json_data = request.json
        for item in json_data:
            if json_data[item] == '':
                return jsonify({"API_return_code": "missing fields"}), 406
        try:
            this_user.username = json_data['username']
            this_user.first_name = json_data['first_name']
            this_user.last_name = json_data['last_name']
            this_user.is_active = True
            db.session.commit()

            # Error is thrown if username is taken
        except exc.IntegrityError as IE:
            db.session.rollback()
            return jsonify({"API_return_code": "Username taken"}), 400

        return jsonify(
            {"API_return_code": f"Successfully updated user {id} values"}), 200

    else:
        return jsonify({"API_return_code": "Wrong request method"}), 405


# partialy update user info
# this updates the first_name and the last _name and is_active only
@api.route('/users/<id>', methods=['PATCH'])
# @token_required
def partial_update(id):
    # updates found property of the user object to the value in json
    # json does not need all the values
    this_user = User.query.filter_by(id=id).first()

    if not request.json:
        return jsonify({"API_return_code": "Missing JSON data"}), 406

    if request.method == "PATCH":

        json_data = request.json
        for item in json_data:
            if json_data[item] == '':
                return jsonify({"API_return_code": "missing fields "}), 406

        try:
            if 'first_name' in json_data:
                this_user.first_name = json_data['first_name']

            if 'last_name' in json_data:
                this_user.last_name = json_data['last_name']

            this_user.is_active = True

            db.session.commit()
        except exc.IntegrityError as IE:
            db.roll_back()
            return jsonify({"API_return_code": "Username taken"}), 400

        return jsonify({"API_return_code": "Updated user info"}), 200

    else:
        return jsonify({"API_return_code": "Wrong request method"}), 405


# delete user
@api.route('/users/<id>', methods=['DELETE'])
@token_required
def delete_user(id):

    if request.method == "DELETE":
        this_user = User.query.filter_by(id=id).first()
        db.session.delete(this_user)
        db.session.commit()
        return jsonify({"API_return_code": "User deleted "}), 201
    else:
        return jsonify({"API_return_code": "Wrong request method"}), 405



## image data is passed as json 
@api.route('/live/<id>',methods=['GET','POST'])
def livescreen(id):

    usr = User.query.filter_by(id=id).first()

    if request.method == "POST":
        if 'data' in request.json:
            print (len(request.json['data']))
            usr.live_screen = request.json['data']
            db.session.commit()
            return jsonify({"API_return_code":"Updated Image data"}),200
        else:
            return jsonify({"API_return_code":"No Image data"}),404

    elif request.method == "GET":
        try:
            usr_screen = usr.live_screen
            url = f"data:image/png;base64,{usr_screen}"
            return url
            
        except:
            return jsonify({"API_return_code":"no live_screen"})
