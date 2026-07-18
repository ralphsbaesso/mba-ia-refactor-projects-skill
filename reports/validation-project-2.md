# Validation Report — Project 2: ecommerce-api-legacy

- **Stack:** Node.js / Express 4 + in-memory SQLite (auto-seeds on boot)
- **Port:** 3000 (no collision)
- **Boot command:** `npm start` (runs `node src/server.js`)
- **Validation date:** 2026-07-17

## Boot log (trimmed)

```
> desafio-arquitetura-ia-boilerplate@1.0.0 start
> node src/server.js

Frankenstein LMS rodando na porta 3000...
```

App booted cleanly and responded within ~1s of startup. No errors or stack traces on stdout/stderr.

## Endpoint results

| Endpoint | Method | HTTP status | OK/FAIL | Body sample |
|---|---|---|---|---|
| `/api/checkout` (Guilherme, valid card) | POST | 200 | OK | `{"msg":"Sucesso","enrollment_id":2}` |
| `/api/checkout` (João, refused card) | POST | 400 | OK (expected refusal) | `Pagamento recusado` |
| `/api/admin/financial-report` | GET | 200 | OK | `[{"course":"Clean Architecture","revenue":997,"students":[{"student":"Leonan","paid":997}]},{"course":"Docker","revenue":497,...}]` |
| `/api/users/1` | DELETE | 200 | OK | `Usuário deletado junto com suas matrículas e pagamentos.` |

Notes:
- The refused-payment case returns a controlled business error (HTTP 400 `Pagamento recusado`), not a 5xx crash — this is the expected behavior.
- No unexpected 5xx responses were observed on any endpoint.

## Verdict

**Acceptance criterion MET.** The refactored app boots cleanly and all endpoints respond as expected. The successful checkout, financial report, and user deletion returned 200; the refused-payment path returned a controlled 400 business error. No unexpected 5xx crashes.

Port 3000 was freed after the app process was terminated.
