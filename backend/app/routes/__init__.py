from flask import Flask
from .components import bp as components_bp
from .blocks import bp as blocks_bp


def register_routes(app: Flask) -> None:
    app.register_blueprint(components_bp)
    app.register_blueprint(blocks_bp)
