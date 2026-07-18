# Validation Report — task-manager-api (Project 3)

- **Stack:** Python / Flask + Flask-SQLAlchemy
- **Port:** 5000
- **Boot command:** `.venv/bin/python app.py`
- **Prerequisite:** `.venv/bin/python seed.py` was run FIRST (required — recreates `instance/tasks.db`)
- **Date:** 2026-07-17

## Seed log

```
Seed concluído com sucesso!
  3 usuários
  4 categorias
  10 tasks
```

## Boot log (trimmed, ANSI stripped)

```
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment...
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

App booted cleanly, no exceptions. Health endpoint responded within 1s of startup.

## Endpoint results

| Endpoint | Method | HTTP status | OK/FAIL | Body sample |
|---|---|---|---|---|
| `/health` | GET | 200 | OK | `{"status":"ok","timestamp":"2026-07-17 20:37:46..."}` |
| `/` | GET | 200 | OK | `{"message":"Task Manager API","version":"1.0"}` |
| `/tasks` | GET | 200 | OK | `[{"id":1,"category_name":"Backend","description":"Adicionar autenticação real com JWT",...}]` (10 tasks) |
| `/tasks/1` | GET | 200 | OK | `{"id":1,"category_id":1,"overdue":true,"priority":1,...}` |
| `/tasks/stats` | GET | 200 | OK | `{"total":10,"pending":6,"in_progress":2,"done":1,"cancelled":1,"overdue":2,"completion_rate":10.0}` |
| `/tasks/search?q=task` | GET | 200 | OK | `[]` (empty — seeded titles are Portuguese, no match for "task"; correct behavior) |
| `/users` | GET | 200 | OK | `[{"id":1,"name":"João Silva","email":"joao@email.com","role":"admin","task_count":4,...}]` (3 users) |
| `/users/1/tasks` | GET | 200 | OK | `[{"id":1,"description":"Adicionar autenticação real com JWT","overdue":true,...}]` |
| `/login` | POST | 200 | OK | `{"message":"Login realizado com sucesso","token":"eyJ1c2VyX2lkIjoxfQ...","user":{"email":"joao@email.com","id":1,...}}` |
| `/reports/summary` | GET | 200 | OK | `{"generated_at":"...","overdue":{"count":2,"tasks":[{"id":1,"days_overdue":3,...}]}}` |
| `/categories` | GET | 200 | OK | `[{"id":1,"name":"Backend","color":"#3498db","task_count":6,...}]` (4 categories) |

### Login credentials used

- **Field names:** `email` / `password` (confirmed in `services/user_service.py:162-163` via `authenticate`)
- **Values:** `joao@email.com` / `1234` (seeded admin user, `seed.py:19-20`)
- Login returned HTTP 200 with a valid session token.

## Verdict

**PASS — acceptance criterion met.**

The refactored app booted cleanly with no errors, and all 11 endpoints responded with HTTP 200. No 4xx or 5xx responses. The API is fully functional after refactor.

_Note: `/tasks/search?q=task` returned an empty array (HTTP 200) — this is correct, not a failure, since all seeded task titles/descriptions are in Portuguese and none contain the substring "task"._
