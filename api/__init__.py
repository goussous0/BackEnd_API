import json
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
            return jsonify({"Error": "Unauthorized"}), 401
        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithm='HS256')

            this_user = User.query.filter_by(id=data['user_id']).first()
            return f(*args, **kwargs)

        except BaseException:
            return jsonify({"Error": "Unauthorized"}), 401

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
        return jsonify({"Error": "No json provided"}), 400

    if request.method == 'POST':

        tmp_user = User.query.filter_by(
            username=request.json['username']).first()
        if not tmp_user:
            return jsonify({"Error": "No such user"}), 404

        # validate user and check provided password
        if check_password_hash(tmp_user.pass_hash, request.json['password']):
            # the user name and password provided are valid
            # generate token

            token = jwt.encode({'user_id': tmp_user.id,
                                'exp': datetime.utcnow() + timedelta(hours=1)},
                               current_app.config['SECRET_KEY'],
                               algorithm='HS256')

            return jsonify(
                {"Error": "Success", "token": token.decode('UTF-8')}), 200
        else:
            return jsonify({"Error": "Forbidden wrong password "}), 403

    else:
        return jsonify({"Error": "Wrong request method"}), 400


# GET request returns all users POST creates new user

@api.route('/users', methods=['GET', 'POST'])
# @token_required
def users():

    all_users = User.query.all()

    # if get then we return the users
    if request.method == "GET":
        users_dict = {}
        # a loop to covert the users object list to a json like format
        for this_user in all_users:
            # username, first_name, last_name, last_login, is_active
            users_dict[this_user.id] = [this_user.username,
                                        this_user.first_name,
                                        this_user.last_name,
                                        str(this_user.last_login),
                                        this_user.is_active]

        json_like = json.dumps(users_dict)

        return jsonify({"Error": json_like}), 200

    # create new user if json data found
    elif request.method == "POST":
        # sample data for valid POST request
        """
                {
                "username": "hello",
                "first_name": "hello",
                "last_name": "world",
                "password": "1234",
                "is_active": true
                }
        """

        if not request.json:
            return jsonify({"Error": "No JSON"}), 401

        json_data = request.json

        for item in json_data:
            if json_data[item] == "":
                return jsonify({"Error": "Can't have empty values"}), 401

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

        except exc.IntegrityError:
            db.session.rollback()
            return jsonify({"Error": "Such username is already registered."})

        return jsonify({"Error": "Added New User."}), 200


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
                 "is_active": user_by_id.is_active}

    return jsonify({"error": json.dumps(this_user)}), 200


# update user info
@api.route('/users/<id>', methods=['PUT'])
@token_required
def update_user(id):
    # updates every property of the user object to the value in json
    # json must have all the values

    # grab the user with specified id
    this_user = User.query.filter_by(id=id).first()
    if not this_user:
        return jsonify({"Error": "No such user"}), 404

    """
    {
        "username": "string",
        "first_name": "string",
        "last_name": "string",
        "password": "string",
        "is_active": true
    }
    """

    if request.method == "PUT":
        json_data = request.json
        for item in json_data:
            if json_data[item] == '':
                return jsonify({"Error": "missing fields"}), 406
        try:
            this_user.username = json_data['username']
            this_user.first_name = json_data['first_name']
            this_user.last_name = json_data['last_name']
            this_user.is_active = json_data['is_active']
            db.session.commit()
        # an error will be thrown if the username is already registred by
        # another user in the db
        except exc.IntegrityError:
            db.roll_back()
            return jsonify({"Error": "Username taken"}), 400

        return jsonify(
            {"Error": f"Successfully updated user {id} values"}), 200

    else:
        return jsonify({"error": "Wrong request method"}), 405


# partialy update user info
# this updates the first_name and the last _name and is_active only
@api.route('/users/<id>', methods=['PATCH'])
@token_required
def partial_update(id):
    # updates found property of the user object to the value in json
    # json does not need all the values
    this_user = User.query.filter_by(id=id).first()

    if not request.json:
        return jsonify({"Error": "Missing JSON data"}), 406

    if request.method == "PATCH":

        json_data = request.json
        for item in json_data:
            if json_data[item] == '':
                return jsonify({"Error": "missing fields "}), 406

        try:
            if json_data['first_name']:
                this_user.first_name = json_data['first_name']

            if json_data['last_name']:
                this_user.last_name = json_data['last_name']

            if json_data['is_active']:
                this_user.is_active = json_data['is_active']

            db.session.commit()
        except exc.IntegrityError:
            db.roll_back()
            return jsonify({"Error": "Username taken"}), 400

        return jsonify({"Error": "Updated user info"}), 200

    else:
        return jsonify({"Error": "Wrong request method"}), 405


# delete user
@api.route('/users/<id>', methods=['DELETE'])
@token_required
def delete_user(id):

    if request.method == "DELETE":
        this_user = User.query.filter_by(id=id).first()
        db.session.delete(this_user)
        return jsonify({"Error": "User deleted "}), 201
    else:
        return jsonify({"Error": "Wrong request method"}), 405
