from flask import jsonify


class ApiError(Exception):
    """Erro de domínio com status HTTP associado.

    Controllers/services levantam esta exceção em vez de montar respostas de erro
    manualmente; o handler central converte em JSON + status apropriado.
    """

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(err):
        return jsonify({"erro": err.message, "sucesso": False}), err.status

    @app.errorhandler(404)
    def handle_not_found(_err):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        # Detalhe vai para o log; o cliente nunca recebe str(e)/stack trace.
        app.logger.exception(err)
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
