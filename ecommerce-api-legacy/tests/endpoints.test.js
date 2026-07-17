const request = require('supertest');
const { openTestDb } = require('./helpers');
const { createApp } = require('../src/app');

let db;
let app;
beforeEach(async () => {
    db = await openTestDb();
    app = createApp(db);
});
afterEach(async () => { await db.close(); });

describe('POST /api/checkout', () => {
    test('sucesso devolve 200 com msg e enrollment_id', async () => {
        const res = await request(app).post('/api/checkout').send({
            usr: 'Guilherme', eml: 'gui@fullcycle.com.br', pwd: 'senhaforte',
            c_id: 2, card: '4111222233334444'
        });
        expect(res.status).toBe(200);
        expect(res.body).toMatchObject({ msg: 'Sucesso' });
        expect(res.body.enrollment_id).toEqual(expect.any(Number));
    });

    test('cartão recusado devolve 400', async () => {
        const res = await request(app).post('/api/checkout').send({
            usr: 'João', eml: 'joao@teste.com', pwd: '123',
            c_id: 1, card: '5111222233334444'
        });
        expect(res.status).toBe(400);
        expect(res.text).toBe('Pagamento recusado');
    });

    test('payload incompleto devolve 400 Bad Request', async () => {
        const res = await request(app).post('/api/checkout').send({ usr: 'x' });
        expect(res.status).toBe(400);
        expect(res.text).toBe('Bad Request');
    });

    test('curso inexistente devolve 404', async () => {
        const res = await request(app).post('/api/checkout').send({
            usr: 'x', eml: 'x@y.com', pwd: 'abc', c_id: 999, card: '4111'
        });
        expect(res.status).toBe(404);
    });
});

describe('GET /api/admin/financial-report', () => {
    test('devolve o relatório no formato legado', async () => {
        const res = await request(app).get('/api/admin/financial-report');
        expect(res.status).toBe(200);
        expect(res.body).toEqual([
            {
                course: 'Clean Architecture',
                revenue: 997.0,
                students: [{ student: 'Leonan', paid: 997.0 }]
            },
            { course: 'Docker', revenue: 0, students: [] }
        ]);
    });
});

describe('DELETE /api/users/:id', () => {
    test('deleta usuário existente com cascata', async () => {
        const res = await request(app).delete('/api/users/1');
        expect(res.status).toBe(200);
        expect(await db.all('SELECT * FROM enrollments WHERE user_id = 1')).toHaveLength(0);
    });

    test('usuário inexistente devolve 404', async () => {
        const res = await request(app).delete('/api/users/999');
        expect(res.status).toBe(404);
    });
});

describe('regressão CRITICAL: secrets fora do código', () => {
    test('config lê PORT e PAYMENT_GATEWAY_KEY do ambiente', () => {
        jest.resetModules();
        process.env.PORT = '4567';
        process.env.PAYMENT_GATEWAY_KEY = 'pk_test_env';
        const config = require('../src/config');
        expect(config.port).toBe(4567);
        expect(config.paymentGatewayKey).toBe('pk_test_env');
        delete process.env.PORT;
        delete process.env.PAYMENT_GATEWAY_KEY;
    });

    test('nenhum arquivo de src/ contém a chave live ou a senha de produção legadas', () => {
        const fs = require('node:fs');
        const path = require('node:path');
        const srcDir = path.join(__dirname, '..', 'src');
        const files = [];
        (function walk(dir) {
            for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
                const full = path.join(dir, entry.name);
                entry.isDirectory() ? walk(full) : files.push(full);
            }
        })(srcDir);
        for (const file of files) {
            const content = fs.readFileSync(file, 'utf8');
            expect(content).not.toMatch(/pk_live_/);
            expect(content).not.toMatch(/senha_super_secreta/);
        }
    });
});
