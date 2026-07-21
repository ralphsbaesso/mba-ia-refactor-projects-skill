# Catálogo de Anti-Patterns

Escala de severidade (baseada em MVC + SOLID):

- **CRITICAL** — falha grave de arquitetura ou segurança: impede funcionamento correto, expõe dados sensíveis (credenciais hardcoded, SQL Injection) ou destrói completamente a separação de responsabilidades (God Class com banco + negócio + rotas).
- **HIGH** — forte violação de MVC/SOLID que compromete manutenção e testes: regra de negócio em controllers/rotas, acoplamento sem injeção de dependência, estado global mutável.
- **MEDIUM** — padronização, duplicação ou performance moderada: N+1, validações ausentes, middlewares mal usados.
- **LOW** — legibilidade: nomes ruins, magic numbers, imports mortos, `print` como log.

Para cada item: **sinais de detecção** (grep-áveis) e severidade. Todo finding cita `arquivo:linha` exatos.

---

## 1. Hardcoded Credentials / Secrets — CRITICAL

Credenciais, chaves e secrets embutidos no código-fonte.

**Sinais**: `SECRET_KEY = "..."` literal; `password`/`pass`/`pwd`/`senha` com valor literal; chaves `pk_live_...`/`sk_...`; credenciais SMTP/DB em objetos de config no código; secret devolvido em endpoint (ex.: health check que ecoa `secret_key`).

## 2. SQL Injection (query montada por concatenação/interpolação) — CRITICAL

**Sinais**: `"SELECT ... " + variavel`, f-strings/template literals com input do usuário dentro de SQL, `LIKE '%" + termo + "%'`; endpoint que executa SQL arbitrário vindo do request. **Correto**: placeholders (`?`, `%s`) ou ORM.

## 3. God Class / God Module — CRITICAL

Um arquivo/classe concentra múltiplas responsabilidades (conexão DB + schema + rotas + regra de negócio + validação) e/ou múltiplos domínios.

**Sinais**: arquivo com centenas de linhas cobrindo várias entidades; classe `*Manager`/`*Handler` que cria banco, registra rotas e processa pagamento; `models.py` com SQL + validação + formatação de 4 domínios.

## 4. Armazenamento inseguro de senhas — CRITICAL

**Sinais**: senha em texto plano no banco ou no seed; comparação `senha == input`; MD5/SHA1 sem salt (`hashlib.md5`); "cripto" caseira (loops de base64); senha incluída em respostas de API (`to_dict` que serializa `password`). **Correto**: bcrypt/scrypt/argon2 (`werkzeug.security`, `crypto.scrypt`).

## 5. Regra de negócio em Controller/Rota (Fat Controller) — HIGH

**Sinais**: handler de rota com dezenas de linhas de validação, cálculo, agregação ou efeitos colaterais (envio de e-mail via `print`, notificações); rota que monta relatórios iterando queries; validações duplicadas entre handlers.

## 6. Estado global mutável / Singleton implícito — HIGH

**Sinais**: `global conexao` para DB compartilhada (pior com `check_same_thread=False`); dicionários de cache globais no módulo; contadores globais; estado de aplicação em variáveis de módulo.

## 7. Ausência de camadas / acoplamento direto — HIGH

Rotas registradas manualmente uma a uma no entry point, handlers acessando o banco diretamente, ausência de injeção de dependência.

**Sinais**: `app.add_url_rule(...)` em lote no entry point; `get_db()` chamado dentro de handler HTTP; entry point que também define rotas de negócio.

## 8. Callback Hell / controle de fluxo assíncrono manual — HIGH

**Sinais** (Node): callbacks aninhados 4+ níveis; contadores manuais de "pendências" (`coursesPending--`) para saber quando responder; `let self = this`. **Correto**: promises + `async/await`.

## 9. Queries N+1 — MEDIUM

**Sinais**: query dentro de `for`/`forEach` sobre resultado de outra query (buscar itens de cada pedido, usuário de cada matrícula, um a um). **Correto**: JOIN ou eager loading.

## 10. Tratamento de erros ausente ou genérico — MEDIUM

**Sinais**: `try/except` (ou `try/catch`) repetido em todo handler devolvendo `str(e)` ao cliente (vaza internals); `except:` bare engolindo erros; ausência de error handler centralizado; erro de DB ignorado no callback.

## 11. Validação ausente ou duplicada — MEDIUM

**Sinais**: endpoints que aceitam qualquer payload; a mesma sequência de `if` de validação copiada em vários handlers; regex de e-mail frouxa; regra de senha mínima fraca (< 8).

## 12. Configuração hardcoded (não-secreta) — MEDIUM

Porta, path do banco, `DEBUG=True`, ambiente fixos no código.

**Sinais**: `app.run(debug=True)`, `port = 3000` literal, `db_path = "loja.db"` no módulo. **Correto**: módulo `config/` lendo variáveis de ambiente com defaults.

## 13. Magic numbers / strings — LOW

**Sinais**: limiares numéricos sem nome (`if faturamento > 10000: desconto = 0.1`); listas de status/categorias repetidas inline em vários pontos.

## 14. Nomenclatura ruim / código morto / print-log — LOW

**Sinais**: variáveis de 1–3 letras (`u`, `e`, `cc`), mistura de idiomas, sombreamento de builtins (`id`); imports não usados (`import os, sys, json` sem uso); helpers definidos e nunca chamados; `print()`/`console.log` como mecanismo de log.

---

## 15. APIs Deprecated (verificação obrigatória)

Identificar uso de APIs obsoletas e **recomendar o equivalente moderno**. Severidade: MEDIUM por padrão (HIGH se já removida na versão instalada). Se nada for encontrado, registrar "Nenhuma API deprecated detectada".

| API deprecated | Contexto | Equivalente moderno |
|---|---|---|
| `datetime.utcnow()` / `datetime.utcfromtimestamp()` | Python ≥ 3.12 (deprecado) | `datetime.now(timezone.utc)` |
| `Model.query.get(id)` / `Query.get()` | SQLAlchemy 2.x (legacy) | `db.session.get(Model, id)` |
| `@app.before_first_request` | Flask ≥ 2.3 (removido) | inicialização no factory / `with app.app_context()` |
| `new Buffer(...)` | Node.js | `Buffer.from(...)` |
| `util.isArray`, `fs.exists` | Node.js | `Array.isArray`, `fs.access`/`fs.stat` |
| `sqlite3` com API de callbacks | Node (legado, propenso a callback hell) | `node:sqlite`, `better-sqlite3` ou wrapper promisificado |
| `body-parser` standalone | Express ≥ 4.16 | `express.json()` embutido |
| `React.createClass`, lifecycle `componentWillMount` | React | classes ES6 / hooks |
| `md5`/`sha1` para senhas | qualquer stack | bcrypt / scrypt / argon2 |

Procure também `DeprecationWarning` ao rodar a aplicação — warnings de boot contam como sinal.
