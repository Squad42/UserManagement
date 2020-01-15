from flask import Flask
import os


app = Flask(__name__)
app.config.from_object("userManagement.server_config.DevelopmentConfig")

from userManagement.server_views import *

if __name__ == "__main__":
    app.run(host="0.0.0.0")
