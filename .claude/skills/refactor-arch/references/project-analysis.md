# Heurísticas de Análise de Projeto (Fase 1)

Detecção de linguagem, framework, banco de dados e arquitetura — agnóstica de tecnologia. Sempre confirme lendo os arquivos; nunca assuma pela extensão apenas.

## 1. Linguagem

| Sinal | Linguagem |
|---|---|
| `*.py`, `requirements.txt`, `pyproject.toml`, `Pipfile` | Python |
| `*.js`/`*.ts`, `package.json` | JavaScript / TypeScript (Node.js) |
| `*.rb`, `Gemfile` | Ruby |
| `*.php`, `composer.json` | PHP |
| `*.go`, `go.mod` | Go |
| `*.java`/`*.kt`, `pom.xml`, `build.gradle` | Java / Kotlin |
| `*.cs`, `*.csproj` | C# |

Se houver mais de uma, a linguagem principal é a do entry point do servidor.

## 2. Framework e versão

Leia o manifesto de dependências — a versão exata está lá:

| Manifesto | Onde olhar |
|---|---|
| `requirements.txt` | linha `flask==3.1.1`, `fastapi==...`, `django==...` |
| `package.json` | `dependencies`: `express`, `fastify`, `koa`, `@nestjs/core` |
| `Gemfile` | `gem 'rails'`, `gem 'sinatra'` |
| `composer.json` | `laravel/framework`, `symfony/*` |
| `go.mod` | `gin-gonic/gin`, `labstack/echo` |

Confirme no código: `Flask(__name__)`, `express()`, `FastAPI()`, etc. Liste também dependências relevantes (CORS, ORM, clients).

## 3. Banco de dados

| Sinal no código | Banco / acesso |
|---|---|
| `import sqlite3`, `sqlite3.connect(...)` | SQLite via driver bruto (SQL manual) |
| `require('sqlite3')`, `new sqlite3.Database(...)` | SQLite (Node, API de callbacks) |
| `flask_sqlalchemy`, `db.Model` | SQLAlchemy (ORM) |
| `psycopg2`, `pg`, `mysql2`, `pymongo`, `mongoose` | Postgres / MySQL / MongoDB |
| `:memory:` como path | banco em memória (dados se perdem no restart — anote!) |

Mapeie as **tabelas/entidades**: procure `CREATE TABLE`, classes `db.Model`, migrations. Anote se há seed automático e se ele é pré-condição para os endpoints funcionarem.

## 4. Domínio da aplicação

Deduza pelos substantivos de tabelas, rotas e entidades:

- `produtos`, `pedidos`, `itens_pedido`, `estoque` → E-commerce
- `courses`, `enrollments`, `payments` → LMS / plataforma de cursos (com checkout)
- `tasks`, `categories`, `users`, prioridade/status → Task manager
- `posts`, `comments` → blog/social

## 5. Mapeamento de arquitetura

Responda: **onde vivem** (a) roteamento, (b) regra de negócio, (c) acesso a dados, (d) configuração, (e) tratamento de erros?

Classificações típicas:

| Padrão observado | Classificação |
|---|---|
| Tudo em 1–5 arquivos na raiz, sem diretórios de camada | **Monolito sem camadas** |
| Uma classe/módulo concentra DB + rotas + negócio | **God Class** (monolito orientado a objeto) |
| Existem `models/`, `routes/`, `services/`, mas rotas contêm regra de negócio pesada | **Camadas parciais** (estrutura existe, disciplina não) |
| Camadas completas e finas | MVC adequado |

Atenção a falsos amigos: um arquivo chamado `controllers.py` ou `models.py` não garante a responsabilidade correta — leia o conteúdo. (Ex.: `models.py` cheio de SQL + validação + regra de negócio é God Module, não camada Model.)

Conte os arquivos-fonte analisados (excluindo dependências, artefatos de banco e caches) — o número entra no resumo da Fase 1.

## 6. Como a aplicação sobe (importante para a Fase 3)

Identifique e anote:

- Comando de boot (`python app.py`, `npm start` — leia `scripts` do package.json / bloco `__main__`)
- Porta (hardcoded? env?)
- Pré-requisitos de boot (seed manual? criação automática de schema?)
- Inventário completo de **endpoints** (método + path) — essa lista é o contrato que a validação da Fase 3 deve reproduzir.
