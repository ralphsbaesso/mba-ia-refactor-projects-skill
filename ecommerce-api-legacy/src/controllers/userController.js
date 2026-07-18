const userService = require('../services/userService');

async function deleteUser(req, res, next) {
    try {
        await userService.deleteUser(req.app.locals.db, req.params.id);
        res.send('Usuário deletado junto com suas matrículas e pagamentos.');
    } catch (err) {
        next(err);
    }
}

module.exports = { deleteUser };
