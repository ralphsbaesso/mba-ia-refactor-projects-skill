const userModel = require('../models/userModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const auditLogModel = require('../models/auditLogModel');
const { ApiError } = require('../middlewares/errorHandler');

// Deleção em cascata: remove pagamentos e matrículas junto com o usuário,
// evitando os registros órfãos do código legado.
async function deleteUser(db, id) {
    const user = await userModel.findById(db, id);
    if (!user) throw new ApiError('Usuário não encontrado', 404);

    await paymentModel.deleteByUserId(db, id);
    await enrollmentModel.deleteByUserId(db, id);
    await userModel.deleteById(db, id);
    await auditLogModel.record(db, `Usuário ${id} deletado com matrículas e pagamentos`);
}

module.exports = { deleteUser };
