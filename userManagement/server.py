from flask import Flask
from userManagement.models import db
from userManagement.example_data import db_load_example_data

app = Flask(__name__)
app.config.from_object("userManagement.server_config.DevelopmentConfig")

if app.config["DB_INITIALIZE"] == "True":

    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DATABASE_CONNECTION_URI"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.app_context().push()

    # ORDERING OF NEXT LINES IS IMPORTANT !!!
    db.init_app(app)
    from userManagement.models import Users

    db.create_all()
    db_load_example_data(app, db)

    app.config["DB_ONLINE"] = True

from userManagement.server_views import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
