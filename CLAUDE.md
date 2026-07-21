# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is a **course challenge scaffold**, not a running application. The deliverable is a Claude Code skill named `refactor-arch` that analyzes, audits, and refactors *any* codebase into MVC — technology-agnostic. Per the challenge spec, the skill lives as **three identical copies inside each target project** (`<project>/.claude/skills/refactor-arch/`) — there is no root copy. Its Step 0 targets the **current working directory** (no argument): run it from inside the project (`cd <project> && claude "/refactor-arch"`). If you edit one copy, replicate it to the other two. The three subdirectories are **legacy target projects** the skill must work against; they are intentionally full of anti-patterns and are inputs, not code to be improved by hand. Read `README.md` (Portuguese) for the full spec, severity scale (CRITICAL/HIGH/MEDIUM/LOW), and acceptance criteria.

The skill runs three sequential phases: **Phase 1** (detect stack + map architecture), **Phase 2** (audit against an anti-pattern catalog, emit a report, then *pause for `[y/n]` confirmation before touching any file*), **Phase 3** (refactor to MVC + validate the app still boots and endpoints respond). Phase 2's confirmation gate and Phase 3's runtime validation are hard requirements.

## The three target projects

Each is deliberately structured at a different level of decay, so the skill must adapt rather than apply one fixed transformation:

| Project | Stack | State | Notable planted problems |
|---|---|---|---|
| `code-smells-project/` | Python / Flask 3.1 + raw `sqlite3` | Monolith, ~800 LOC in 4 files | Hardcoded `SECRET_KEY` in `app.py`, global mutable DB connection in `database.py`, God-class `models.py`, business logic in `controllers.py` |
| `ecommerce-api-legacy/` | Node.js / Express 4 + `sqlite3` | LMS + checkout in `src/AppManager.js` | Single God-class manager, thin `app.js` entrypoint |
| `task-manager-api/` | Python / Flask 3.0 + Flask-SQLAlchemy | *Partially* organized (`models/ routes/ services/ utils/`) | Already has layers but heavy logic in `routes/`, so "refactor" here means fixing violations, not creating structure |

Key adaptation point: `task-manager-api` already has separation of concerns; the skill must not blindly recreate directories that exist. For it, "works after refactor" = API boots and all endpoints still respond.

## Running the target projects

Each has its own dependencies and boot quirk — get these right or validation fails:

```bash
# code-smells-project (Flask, raw sqlite) — auto-creates & seeds loja.db on first boot
cd code-smells-project && pip install -r requirements.txt && python app.py   # :5000

# ecommerce-api-legacy (Express) — in-memory sqlite, auto-seeds on boot
cd ecommerce-api-legacy && npm install && npm start                          # :3000  (see api.http for requests)

# task-manager-api (Flask-SQLAlchemy) — MUST seed before first boot or endpoints return empty
cd task-manager-api && pip install -r requirements.txt && python seed.py && python app.py   # :5000
```

There is no test suite, linter, or build step in this repo. Validation is behavioral: boot the app and hit its endpoints (curl / `api.http`).

## Working conventions

- The skill name `refactor-arch` and its `SKILL.md` filename are fixed by the spec — do not rename them.
- Reference files backing the skill must be Markdown and must cover all five required knowledge areas: project analysis heuristics, anti-pattern catalog (≥8 patterns incl. deprecated-API detection), audit report template, MVC guidelines, and a refactoring playbook (≥8 before/after transformations).
- Findings must cite exact `file:line`. Deliverable audit reports are saved to `reports/audit-project-{1,2,3}.md`.
- `code-smells-project` and `task-manager-api` both run on port 5000 — run them one at a time.

## Extra: version control

This is a study project. Committing directly to the **main** branch is allowed — there is no need to create a separate branch.
