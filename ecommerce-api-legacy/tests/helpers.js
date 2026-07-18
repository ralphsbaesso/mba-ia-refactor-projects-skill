const { openDatabase } = require('../src/db/connection');
const { initDb } = require('../src/db/schema');

async function openTestDb() {
    const db = openDatabase(':memory:');
    await initDb(db);
    return db;
}

module.exports = { openTestDb };
