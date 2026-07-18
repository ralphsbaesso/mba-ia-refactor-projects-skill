const config = require('./config');
const { openDatabase } = require('./db/connection');
const { initDb } = require('./db/schema');
const { createApp } = require('./app');

async function main() {
    const db = openDatabase(config.dbPath);
    await initDb(db);

    const app = createApp(db);
    app.listen(config.port, () => {
        console.log(`Frankenstein LMS rodando na porta ${config.port}...`);
    });
}

main().catch((err) => {
    console.error('Falha ao iniciar a aplicação:', err);
    process.exit(1);
});
