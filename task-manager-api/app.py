"""Composition root: monta o app, injeta config, registra rotas e error handler."""
from datetime import datetime

from flask import Flask
from flask_cors import CORS

from config.settings import Config
from database import db
from middlewares.error_handler import register_error_handlers


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    CORS(app)
    db.init_app(app)

    from routes.report_routes import report_bp
    from routes.task_routes import task_bp
    from routes.user_routes import user_bp

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    register_error_handlers(app)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(datetime.now())}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
