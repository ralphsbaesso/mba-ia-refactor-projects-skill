const { openTestDb } = require('./helpers');
const checkoutService = require('../src/services/checkoutService');
const reportService = require('../src/services/reportService');
const userService = require('../src/services/userService');
const { ApiError } = require('../src/middlewares/errorHandler');

let db;
beforeEach(async () => { db = await openTestDb(); });
afterEach(async () => { await db.close(); });

describe('checkoutService', () => {
    const payload = {
        name: 'Gui', email: 'gui@teste.com', password: 'senhaforte',
        courseId: 2, card: '4111222233334444'
    };

    test('caminho feliz: cria usuário, matrícula e pagamento PAID', async () => {
        const result = await checkoutService.checkout(db, payload);
        expect(result.msg).toBe('Sucesso');

        const payment = await db.get(
            'SELECT * FROM payments WHERE enrollment_id = ?', [result.enrollment_id]);
        expect(payment).toMatchObject({ amount: 497.0, status: 'PAID' });
    });

    test('cartão não iniciado em 4 → pagamento recusado (400), sem matrícula', async () => {
        await expect(checkoutService.checkout(db, { ...payload, card: '5111222233334444' }))
            .rejects.toMatchObject({ status: 400, message: 'Pagamento recusado' });
        const enrollment = await db.get(
            'SELECT e.* FROM enrollments e JOIN users u ON u.id = e.user_id WHERE u.email = ?',
            [payload.email]);
        expect(enrollment).toBeUndefined();
    });

    test('curso inexistente → 404', async () => {
        await expect(checkoutService.checkout(db, { ...payload, courseId: 999 }))
            .rejects.toMatchObject({ status: 404, message: 'Curso não encontrado' });
    });

    test('regressão CRITICAL: usuário novo sem senha é rejeitado (sem default "123456")', async () => {
        await expect(checkoutService.checkout(db, { ...payload, password: undefined }))
            .rejects.toBeInstanceOf(ApiError);
    });

    test('usuário existente reutilizado (não duplica cadastro)', async () => {
        await checkoutService.checkout(db, payload);
        await checkoutService.checkout(db, { ...payload, courseId: 1 });
        const rows = await db.all('SELECT id FROM users WHERE email = ?', [payload.email]);
        expect(rows).toHaveLength(1);
    });
});

describe('reportService', () => {
    test('mantém o formato legado e soma revenue apenas de pagamentos PAID', async () => {
        const report = await reportService.financialReport(db);
        expect(report).toEqual([
            {
                course: 'Clean Architecture',
                revenue: 997.0,
                students: [{ student: 'Leonan', paid: 997.0 }]
            },
            { course: 'Docker', revenue: 0, students: [] }
        ]);
    });
});

describe('userService', () => {
    test('regressão HIGH: deleção em cascata não deixa matrículas/pagamentos órfãos', async () => {
        await userService.deleteUser(db, 1);
        expect(await db.get('SELECT * FROM users WHERE id = 1')).toBeUndefined();
        expect(await db.all('SELECT * FROM enrollments WHERE user_id = 1')).toHaveLength(0);
        expect(await db.all('SELECT * FROM payments')).toHaveLength(0);
    });

    test('usuário inexistente → 404', async () => {
        await expect(userService.deleteUser(db, 999))
            .rejects.toMatchObject({ status: 404 });
    });
});
