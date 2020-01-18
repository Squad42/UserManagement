from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), unique=True)
    full_name = db.Column(db.String(20))
    password = db.Column(db.String(100))  # longer due to sha256Hash
    user_since = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    admin = db.Column(db.Boolean)

    def __init__(self, username, full_name, password, user_since, admin):
        self.username = username
        self.full_name = full_name
        self.password = password
        self.user_since = datetime.datetime.strptime(user_since, "%Y-%m-%dT%H:%M:%SZ")
        self.admin = admin
