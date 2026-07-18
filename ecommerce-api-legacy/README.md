# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000` (configurável via `PORT`). O banco SQLite é em memória por padrão (`DB_PATH`) e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

## Testes

```bash
npm test
```

Suíte unitária (jest + supertest) cobrindo models, services e endpoints em `tests/`.
