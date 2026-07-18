"""Error handling centralizado: erros de domínio viram status HTTP; inesperados viram 500 sem vazar internals."""
from flask import jsonify


class ApiError(Exception):
    """Erro de domínio com status HTTP associado."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return jsonify({'error': error.message}), error.status

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        app.logger.exception('Erro não tratado')
        return jsonify({'error': 'Erro interno'}), 500
