import models
import config as Conf

from flask import Flask
from flask_cors import CORS

from tools import Initializer

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = Conf.DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
Conf.DB.app = app
Conf.DB.init_app(app)
Conf.DB.create_all()
Initializer.init_all()

if __name__ == "__main__":
    app.run(host=Conf.APP_DEFAULT_HOST, port=Conf.APP_DEFAULT_PORT)
    #app.run(port=5000)