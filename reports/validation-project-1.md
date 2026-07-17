# Validation Report — code-smells-project (Project 1)

## Summary

- **Project:** `code-smells-project/`
- **Stack:** Python / Flask (raw `sqlite3`), application-factory pattern refactored into MVC (`config/`, `controllers/`, `routes/`, `models/`, `services/`, `database/`, `middlewares/`, `utils/`)
- **Port used:** 5001 (set via `PORT` environment variable — no source files edited)
- **Database:** `loja.db` auto-created and seeded on boot
- **Boot command:**
  ```bash
  PORT=5001 .venv/bin/python app.py
  ```

## Boot log (relevant lines)

```
INFO:app:Servidor iniciado em http://localhost:5001
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5001
 * Running on http://192.168.1.109:5001
INFO:werkzeug:127.0.0.1 - - [17/Jul/2026 20:37:06] "GET /health HTTP/1.1" 200 -
```

App responded to `/health` within ~1 second of boot. No exceptions or tracebacks during startup or request handling. Health check confirms DB connected and seeded (10 produtos, 3 usuarios, 0 pedidos).

## Endpoint results

| Endpoint | Method | HTTP status | OK/FAIL | Body sample |
|---|---|---|---|---|
| `/health` | GET | 200 | OK | `{"ambiente":"development","counts":{"pedidos":0,"produtos":10,"usuarios":3},"database":"connected","status":"ok","versao":"1.0.0"}` |
| `/` | GET | 200 | OK | `{"endpoints":{"health":"/health","login":"/login","pedidos":"/pedidos","produtos":"/produtos","relatorios":"/relatorios/vendas","usuarios":"/usuarios"},"mensagem":"Bem-vindo à API da Loja"}` |
| `/produtos` | GET | 200 | OK | `{"dados":[{"id":1,"nome":"Notebook Gamer","preco":5999.99,"estoque":10,"categoria":"informatica",...}],...}` |
| `/produtos/1` | GET | 200 | OK | `{"dados":{"id":1,"nome":"Notebook Gamer","preco":5999.99,...},"sucesso":true}` |
| `/usuarios` | GET | 200 | OK | `{"dados":[{"id":1,"nome":"Admin","email":"admin@loja.com","tipo":"admin",...}],...}` |
| `/login` | POST | 200 | OK | Request body `{"email":"admin@loja.com","senha":"admin123"}` → `{"dados":{"id":1,"nome":"Admin","email":"admin@loja.com","tipo":"admin"},"mensagem":"Login OK","sucesso":true}` |
| `/pedidos` | GET | 200 | OK | `{"dados":[],"sucesso":true}` |
| `/relatorios/vendas` | GET | 200 | OK | `{"dados":{"total_pedidos":0,"faturamento_bruto":0,"faturamento_liquido":0,"ticket_medio":0,...},"sucesso":true}` |

**Login field names used:** `email` and `senha` (JSON body). These match the login handler in `controllers/usuario_controller.py` (`dados.get("email")`, `dados.get("senha")`) — the requested keys were correct, no adjustment needed.

## Verdict

**PASS.** The app booted cleanly on port 5001 with no errors, and all 8 endpoints responded with HTTP 200 (expected 2xx). No 5xx errors observed. The acceptance criterion **"app works after refactor"** is met for `code-smells-project`.
