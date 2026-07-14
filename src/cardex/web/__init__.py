from cardex.config import load_database_config
from cardex.db import pool
from flask import Flask
from flask_cors import CORS

from .routes import bp


def create_app(config=None):
    app = Flask(__name__)
    CORS(app)

    config = config or load_database_config("config.ini")
    app.config["DB"] = config

    pool.open()

    app.register_blueprint(bp)

    return app
