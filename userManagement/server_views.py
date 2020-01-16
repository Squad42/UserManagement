from userManagement.server import app
from userManagement.models import Users
from userManagement.manage_db import get_all, add_instance, delete_instance, edit_instance
from flask import Flask, jsonify, request, make_response, session, g
import jwt
import json
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash


def jwt_token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):

        if "jwt_token" not in session:
            return jsonify({"message": "Auth token is missing!"}), 403

        token = session["jwt_token"]

        if not token:
            return jsonify({"message": "Unknown token type!"}), 403

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
            g.user = data
            app.logger.info("Logged in user: %s", g.user["username"])
        except:
            return jsonify({"message": "Token is invalid!"}), 403

        return func(*args, **kwargs)

    return decorated


@app.route("/login")
def login():

    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response(
            "Could not verify", 401, {"WWW-Authenticate": 'Basic realm="Login required!"'}
        )

    user = Users.query.filter_by(username=auth.username).first()

    if not user:
        return make_response(
            "Invalid credentials!", 401, {"WWW-Authenticate": 'Basic realm="Login required!"'}
        )

    # TODO: REMOVE SECOND CHECK - FOR SAFETY REASONS - devtest allows no hash
    if check_password_hash(user.password, auth.password) or user.password == auth.password:
        token = jwt.encode(
            {
                "username": auth.username,
                "role": "basic",
                "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
            },
            app.config["SECRET_KEY"],
        )
        session["jwt_token"] = token
        session["logged_in_user"] = user.username

        return jsonify({"token": token.decode("UTF-8")})

    return make_response(
        "Could not verify!", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )


@app.route("/users", methods=["GET"])
# def get_all_users(current_user):
def get_all_users():

    # TODO: swtich to session not g
    # user = g.user
    # if not current_user.admin:
    #     return jsonify({'message' : 'Cannot perform that function!'})

    users = Users.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data["username"] = user.username
        user_data["full_name"] = user.full_name
        user_data["password"] = user.password
        user_data["user_since"] = user.user_since
        user_data["admin"] = user.admin
        output.append(user_data)

    return jsonify({"users": output})


@app.route("/users/add", methods=["POST"])
def create_user():

    if not app.config["DB_ONLINE"]:
        print("ERROR: Database connection is down!")
        response = jsonify(service_status="Bad gateway: check DB connection!", service_code=502)
        return response, 200

    # TODO: swtich to session not g
    # user = g.user
    # if not current_user.admin:
    # return jsonify({'message' : 'Cannot perform that function!'})

    data = request.get_json()

    username = data["username"]
    full_name = data["full_name"]
    password = data["password"]
    # user_since = data["user_since"]
    # admin = data["admin"]
    user_since = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    admin = False

    hashed_password = generate_password_hash(password, method="sha256")

    add_instance(
        Users,
        username=username,
        full_name=full_name,
        password=hashed_password,
        user_since=user_since,
        admin=admin,
    )

    return json.dumps("Added"), 200


@app.route("/users/promote/<username>", methods=["PATCH"])
def edit(username):

    if not app.config["DB_ONLINE"]:
        print("ERROR: Database connection is down!")
        response = jsonify(service_status="Bad gateway: check DB connection!", service_code=502)
        return response, 200

    data = request.get_json()
    now_admin = True
    edit_instance(Users, username=username, admin=now_admin)

    return json.dumps("Edited"), 200


@app.route("/users/remove/<username>", methods=["DELETE"])
def remove(username):

    if not app.config["DB_ONLINE"]:
        print("ERROR: Database connection is down!")
        response = jsonify(service_status="Bad gateway: check DB connection!", service_code=502)
        return response, 200

    delete_instance(Users, username=username)

    return json.dumps("Deleted"), 200


@app.route("/users/info", methods=["GET"])
def user():

    if "logged_in_user" in session:
        return session["logged_in_user"]

    return "Unknown user"
