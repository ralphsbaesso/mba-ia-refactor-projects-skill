class ApiError extends Error {
    constructor(message, status = 400) {
        super(message);
        this.status = status;
    }
}

// Middleware de erro centralizado do Express (registrado por último).
// Erros de domínio viram o status/mensagem apropriados; erros inesperados
// viram 500 sem vazar internals para o cliente.
function errorHandler(err, req, res, next) { // eslint-disable-line no-unused-vars
    if (err instanceof ApiError) {
        return res.status(err.status).send(err.message);
    }
    console.error('[ERROR]', err);
    return res.status(500).send('Erro interno');
}

module.exports = { ApiError, errorHandler };
