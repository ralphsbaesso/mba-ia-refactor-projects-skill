import logging

from flask import Flask
from flask_cors import CORS

from config import Config
from database import close_db, init_db
from middlewares import register_error_handlers
from routes import register_routes


def create_app(overrides=None):
    """Application factory (composition root): monta config, DB, rotas e error handlers."""
    app = Flask(__name__)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)

    logging.basicConfig(level=logging.INFO)
    CORS(app)

    app.teardown_appcontext(close_db)
    register_error_handlers(app)
    register_routes(app)
    init_db(app)

    return app


app = create_app()


if __name__ == "__main__":
    app.logger.info("Servidor iniciado em http://localhost:%s", app.config["PORT"])
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
