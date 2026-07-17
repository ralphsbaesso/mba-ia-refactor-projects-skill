const { openTestDb } = require('./helpers');
const courseModel = require('../src/models/courseModel');
const userModel = require('../src/models/userModel');
const { hashPassword, verifyPassword } = require('../src/services/passwordService');

let db;
beforeEach(async () => { db = await openTestDb(); });
afterEach(async () => { await db.close(); });

describe('courseModel', () => {
    test('findActiveById retorna curso ativo do seed', async () => {
        const course = await courseModel.findActiveById(db, 1);
        expect(course).toMatchObject({ title: 'Clean Architecture', price: 997.0, active: 1 });
    });

    test('findActiveById retorna undefined para curso inexistente', async () => {
        expect(await courseModel.findActiveById(db, 999)).toBeUndefined();
    });
});

describe('userModel', () => {
    test('create + findByEmail não expõe a senha', async () => {
        const id = await userModel.create(db, {
            name: 'Ana', email: 'ana@teste.com', passwordHash: hashPassword('segredo')
        });
        const user = await userModel.findByEmail(db, 'ana@teste.com');
        expect(user.id).toBe(id);
        expect(user).not.toHaveProperty('pass');
    });

    test('regressão CRITICAL: senha é armazenada com hash scrypt, nunca em texto plano', async () => {
        await userModel.create(db, {
            name: 'Bia', email: 'bia@teste.com', passwordHash: hashPassword('minhasenha')
        });
        const row = await db.get('SELECT pass FROM users WHERE email = ?', ['bia@teste.com']);
        expect(row.pass).not.toBe('minhasenha');
        expect(row.pass).toMatch(/^[0-9a-f]{32}:[0-9a-f]{128}$/);
        expect(verifyPassword('minhasenha', row.pass)).toBe(true);
        expect(verifyPassword('errada', row.pass)).toBe(false);
    });

    test('regressão CRITICAL: seed não guarda senha em texto plano', async () => {
        const row = await db.get('SELECT pass FROM users WHERE email = ?', ['leonan@fullcycle.com.br']);
        expect(row.pass).not.toBe('123');
        expect(verifyPassword('123', row.pass)).toBe(true);
    });
});
