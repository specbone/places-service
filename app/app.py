import models
import apis
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

app.register_blueprint(apis.CountryAPI.blueprint, url_prefix="/country")
app.register_blueprint(apis.StateAPI.blueprint, url_prefix="/state")
app.register_blueprint(apis.CountyAPI.blueprint, url_prefix="/county")
app.register_blueprint(apis.CityAPI.blueprint, url_prefix="/city")
app.register_blueprint(apis.TaskAPI.blueprint, url_prefix="/task")

if __name__ == "__main__":
    app.run(host=Conf.APP_DEFAULT_HOST, port=Conf.APP_DEFAULT_PORT)
    #app.run(port=5000)