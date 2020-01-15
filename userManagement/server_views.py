from userManagement.server import app
from flask import Flask, jsonify, request, make_response, session
import jwt
import datetime
from functools import wraps


users = ["max", "low"]
passwords = {"max": "secret", "low": "secret"}


@app.route("/login")
def login():
    auth = request.authorization

    if auth:

        if auth.username in users and auth.password == passwords[auth.username]:
            token = jwt.encode(
                {
                    "username": auth.username,
                    "role": "basic",
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
                },
                app.config["SECRET_KEY"],
            )
            session["jwt_token"] = token
            return jsonify({"token": token.decode("UTF-8")})
        else:
            return make_response(
                "Invalid credentials!", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'}
            )

    return make_response(
        "Could not verify!", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )

