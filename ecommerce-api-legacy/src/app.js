const express = require('express');
const routes = require('./routes');
const { errorHandler } = require('./middlewares/errorHandler');

// Composition root: monta o app com o banco injetado, sem chamar listen
// (o listen fica em server.js; testes usam supertest direto no app).
function createApp(db) {
    const app = express();
    app.use(express.json());
    app.locals.db = db;
    app.use(routes);
    app.use(errorHandler);
    return app;
}

module.exports = { createApp };
