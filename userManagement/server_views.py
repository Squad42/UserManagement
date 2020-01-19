import json
from flask import Flask, jsonify, request, make_response, session, g
from userManagement.server import app
from userManagement.models import Users
from userManagement.manage_db import get_all, add_instance, delete_instance, edit_instance
from functools import wraps
import jwt
import datetime
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


@app.route("/users/logout", methods=["GET"])
def logout():

    try:
        [session.pop(key) for key in list(session.keys())]
        return json.dumps("User logged out"), 200
    except:
        return json.dumps("User log out attempt failed!"), 304


@app.route("/users/login")
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


@app.route("/users/login_credentials_check", methods=["POST"])
def login_credentials():

    data = request.json

    username = data["username"]
    password = data["password"]

    if not username or not password:
        return make_response(
            "Could not verify", 401, {"WWW-Authenticate": 'Basic realm="Login required!"'}
        )

    user = Users.query.filter_by(username=username).first()

    if not user:
        return make_response(
            "Invalid credentials!", 401, {"WWW-Authenticate": 'Basic realm="Login required!"'}
        )

    # TODO: REMOVE SECOND CHECK - FOR SAFETY REASONS - devtest allows no hash
    if check_password_hash(user.password, password) or user.password == password:
        token = jwt.encode(
            {
                "username": username,
                "role": "basic",
                "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
            },
            app.config["SECRET_KEY"],
        )
        session["jwt_token"] = token
        session["logged_in_user"] = user.username

        return jsonify({"jwt_token": token.decode("UTF-8"), "logged_in_user": user.username}), 200

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
    user_since = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    admin = False

    hashed_password = generate_password_hash(password, method="sha256")

    if not username or not password:
        json.dumps("ERROR: Insufficent credentials!"), 403

    if not Users.query.filter_by(username=username).first():
        add_instance(
            Users,
            username=username,
            full_name=full_name,
            password=hashed_password,
            user_since=user_since,
            admin=admin,
        )

        return json.dumps("Added"), 200

    return json.dumps("ERROR: User with provided username already exists!"), 403


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

@app.route("/health/liveness")
def liveness():
    healthStatus = None
    try:
        if "consul_server" in app.config and app.config["consul_server"] is not None:
            index = None
            index, data = app.config["consul_server"].kv.get("userManagement/alive", index=index)
            if data is not None:
                healthStatus = data["Value"]
            else:
                healthStatus = "true"
        else:
            healthStatus = "true"
    except:
        healthStatus = "false"        

    if "false" in str(healthStatus).lower():
        response = jsonify(
        service_status="FAIL",
        service_code=503)
        return response, 503
    else:
        response = jsonify(
        service_status="PASS",
        service_code=200)
        return response, 200
    
@app.route("/health/readiness")
def readiness():
    healthStatus = None
    try:
        if "consul_server" in app.config and app.config["consul_server"] is not None:
            index = None
            index, data = app.config["consul_server"].kv.get("userManagement/ready", index=index)
            if data is not None:
                healthStatus = data["Value"]
            else:
                healthStatus = "true"
        else:
            healthStatus = "true"
    except:
        healthStatus = "false"         

    if "false" in str(healthStatus).lower():
        response = jsonify(
        service_status="FAIL",
        service_code=503)
        return response, 503
    else:
        response = jsonify(
        service_status="PASS",
        service_code=200)
        return response, 200  