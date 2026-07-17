const courseModel = require('../models/courseModel');
const userModel = require('../models/userModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const auditLogModel = require('../models/auditLogModel');
const { hashPassword } = require('./passwordService');
const { ApiError } = require('../middlewares/errorHandler');

// Regra do gateway simulado (comportamento legado preservado):
// cartões iniciados em "4" são aprovados, demais recusados.
const APPROVED_CARD_PREFIX = '4';

const PAYMENT_STATUS = { PAID: 'PAID', DENIED: 'DENIED' };

function processPayment(card) {
    return card.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
}

async function checkout(db, { name, email, password, courseId, card }) {
    const course = await courseModel.findActiveById(db, courseId);
    if (!course) throw new ApiError('Curso não encontrado', 404);

    let user = await userModel.findByEmail(db, email);
    let userId;
    if (!user) {
        if (!password) throw new ApiError('Bad Request', 400);
        userId = await userModel.create(db, { name, email, passwordHash: hashPassword(password) });
    } else {
        userId = user.id;
    }

    const status = processPayment(card);
    if (status === PAYMENT_STATUS.DENIED) throw new ApiError('Pagamento recusado', 400);

    const enrollmentId = await enrollmentModel.create(db, userId, courseId);
    await paymentModel.create(db, enrollmentId, course.price, status);
    await auditLogModel.record(db, `Checkout curso ${courseId} por ${userId}`);

    return { msg: 'Sucesso', enrollment_id: enrollmentId };
}

module.exports = { checkout, processPayment, PAYMENT_STATUS };
