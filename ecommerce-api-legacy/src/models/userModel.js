function findByEmail(db, email) {
    return db.get('SELECT id, name, email FROM users WHERE email = ?', [email]);
}

function findById(db, id) {
    return db.get('SELECT id, name, email FROM users WHERE id = ?', [id]);
}

async function create(db, { name, email, passwordHash }) {
    const result = await db.run(
        'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        [name, email, passwordHash]
    );
    return result.lastID;
}

function deleteById(db, id) {
    return db.run('DELETE FROM users WHERE id = ?', [id]);
}

module.exports = { findByEmail, findById, create, deleteById };
