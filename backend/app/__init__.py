import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from .db import db

load_dotenv()


def create_app(test_config: dict = None):
    app = Flask(__name__)
    CORS(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from .routes import register_routes
    register_routes(app)

    return app
