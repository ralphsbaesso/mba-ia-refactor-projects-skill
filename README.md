# refactor-arch — Refatoração Arquitetural Automatizada com Claude Code

Skill do Claude Code que **analisa, audita e refatora qualquer codebase para o padrão MVC**, de forma agnóstica de tecnologia. Este repositório entrega a skill (`.claude/skills/refactor-arch/`) e o resultado da sua execução sobre três projetos legados de stacks e níveis de organização diferentes.

> O enunciado original do desafio está preservado em [`docs/CHALLENGE.md`](docs/CHALLENGE.md).

## Abordagem de invocação: skill única na raiz + diretório-alvo

O enunciado sugere **copiar** a pasta da skill para dentro de cada projeto. Optei por **não replicar** a skill: existe **uma única cópia na raiz** do repositório e o sub-projeto alvo é passado como **argumento obrigatório**.

```bash
# a partir da raiz do repositório
claude "/refactor-arch code-smells-project"
claude "/refactor-arch ecommerce-api-legacy"
claude "/refactor-arch task-manager-api"
```

Isso é implementado no **Passo 0** do `SKILL.md`, que lê `$ARGUMENTS`, valida o diretório e define `TARGET` — todas as fases atuam **somente** dentro de `TARGET/` (a única escrita fora dele é o relatório em `reports/`):

- Sem argumento → a skill **para imediatamente** e imprime a mensagem de uso com a lista de sub-projetos disponíveis.
- Diretório inexistente → a skill **para** com erro.
- `disable-model-invocation: true` no frontmatter garante que só o usuário aciona a skill (o modelo não a dispara sozinho).

**Por que essa abordagem:** uma fonte única de verdade (sem N cópias para manter em sincronia), zero acoplamento a um projeto específico e a mesma prova de agnosticismo — a skill roda nas 3 stacks a partir do mesmo lugar, mudando apenas o argumento.

---

## A) Análise Manual

Problemas identificados manualmente em cada projeto antes de construir a skill (base do catálogo de anti-patterns). A lista completa com `arquivo:linha` está nos relatórios em [`reports/`](reports/).

### Projeto 1 — `code-smells-project` (Python/Flask, raw `sqlite3`)

Monolito de ~800 LOC em 4 arquivos, sem separação de camadas.

| Severidade | Problema | Por que é relevante |
|---|---|---|
| CRITICAL | `SECRET_KEY` hardcoded em `app.py:7` **e ecoada** por `/health` (`controllers.py:289`) | Secret no VCS + exposto por endpoint público → sessões forjáveis |
| CRITICAL | SQL Injection por concatenação em ~todas as queries (`models.py`) | Bypass de auth no `/login`, leitura/escrita arbitrária |
| CRITICAL | `/admin/query` executa SQL arbitrário do request (`app.py:59-78`) | Equivalente a RCE sobre o banco, sem auth |
| CRITICAL | God Module com SQL de 4 domínios (`models.py:1-315`) | Impossível testar/evoluir camadas isoladamente |
| CRITICAL | Senhas em texto plano, gravadas e comparadas via SQL (`database.py`, `models.py`) | Vazamento total de credenciais num dump |
| HIGH | Fat Controller com regra de negócio e efeitos colaterais (`controllers.py`) | Lógica não testável fora do ciclo HTTP; duplicada |
| HIGH | Conexão de DB em estado global (`database.py:4`, `check_same_thread=False`) | Race conditions sob concorrência |
| MEDIUM | Queries N+1 na montagem de pedidos (`models.py:187-231`) | Latência cresce com o volume |
| MEDIUM | `DEBUG=True` e host/porta/db hardcoded (`app.py:8`) | Debugger do Werkzeug exposto em produção |
| LOW | `print()` como log; magic numbers de desconto; `id` sombreando builtin | Legibilidade e manutenção |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express, sqlite3 in-memory)

LMS + checkout numa God Class `AppManager` (~180 LOC).

| Severidade | Problema | Por que é relevante |
|---|---|---|
| CRITICAL | Chave `pk_live` de gateway + senha de DB hardcoded (`src/utils.js:1-7`) e cartão logado (`AppManager.js:45`) | Cobranças reais possíveis; credenciais de produção no repo |
| CRITICAL | God Class `AppManager` (conexão + schema + rotas + negócio) (`AppManager.js:4-139`) | Nenhuma fronteira arquitetural |
| CRITICAL | "Criptografia" caseira `badCrypto()` + senha default `"123456"` (`utils.js:17-23`, `AppManager.js:68`) | Senhas reversíveis; contas com credencial pública |
| HIGH | Fat Controller de checkout (50 linhas na rota) (`AppManager.js:28-78`) | Regra de negócio intestável e não reutilizável |
| HIGH | Callback hell de 5 níveis + `const self = this` (`AppManager.js:37-77`) | Fluxo frágil; erro esquecido pendura a request |
| HIGH | Estado global mutável (`globalCache`, `totalRevenue`) (`utils.js:9-25`) | Cache sem limite; comportamento não determinístico |
| MEDIUM | Queries N+1 no relatório financeiro (`AppManager.js:83-126`) | `1 + C + 2E` queries |
| MEDIUM | Erros de DB ignorados; DELETE responde sucesso mesmo falhando (`AppManager.js:57,133`) | Falhas silenciosas, dados órfãos |
| MEDIUM | `sqlite3` com API de callbacks (deprecated) (`AppManager.js:1`) | Induz o callback hell |
| LOW | Nomes de 1-3 letras, código morto, `console.log` com cartão | Legibilidade; dado sensível em stdout |

### Projeto 3 — `task-manager-api` (Python/Flask + Flask-SQLAlchemy)

Já **parcialmente organizado** (`models/ routes/ services/ utils/`), mas com a lógica presa nas rotas. ~1.160 LOC em 15 arquivos.

| Severidade | Problema | Por que é relevante |
|---|---|---|
| CRITICAL | `SECRET_KEY` + credenciais SMTP hardcoded (`app.py:13`, `notification_service.py:7-10`) | Chave de sessão e e-mail expostas |
| CRITICAL | Senhas em MD5 sem salt **e** `password` serializado em `to_dict()` + token previsível (`models/user.py`, `user_routes.py`) | Rainbow table em segundos; API entrega o hash |
| HIGH | Fat Controller: cálculo de "overdue" copiado em 5 pontos, enquanto `Task.is_overdue()` existe e nunca é chamado | Mudança de regra exige editar 5 arquivos |
| HIGH | Camadas ilusórias: `services/` e `utils/helpers.py` existem mas nenhuma rota os usa | Testabilidade/reuso anulados; código morto |
| MEDIUM | Queries N+1 em `GET /tasks` (`User/Category.query.get` no loop) | ~2N+1 queries com N tasks |
| MEDIUM | `except:` bare em 8 handlers; sem error handler central | Erros reais invisíveis, sem stack trace |
| MEDIUM | `datetime.utcnow()` (18+ usos) e `Model.query.get()` (16 usos) — **deprecated** | Warnings hoje, quebra futura; datetime naive |
| LOW | Imports mortos em todo arquivo; magic strings de status/role duplicadas | Ruído; constantes existentes não usadas |

---

## B) Construção da Skill

### Estrutura do `SKILL.md` e arquivos de referência

A skill segue **progressive disclosure**: o `SKILL.md` é enxuto (orquestração + regras invioláveis) e delega o "como" para arquivos carregados sob demanda por fase.

```
.claude/skills/refactor-arch/
├── SKILL.md          # Passo 0 (validação de argumento) + fluxo das 3 fases + gate [y/n]
├── analyze.md        # Parte 1 → Fase 1 (análise) + Fase 2 (auditoria). SOMENTE LEITURA
├── execute.md        # Parte 2 → Fase 3 (refatoração + testes + validação de runtime)
└── references/
    ├── project-analysis.md      # heurísticas de detecção de linguagem/framework/banco/arquitetura
    ├── anti-patterns.md         # catálogo (15 anti-patterns + tabela de APIs deprecated)
    ├── report-template.md       # template padronizado do relatório da Fase 2
    ├── mvc-guidelines.md        # responsabilidades de cada camada MVC alvo
    ├── refactoring-playbook.md  # transformações antes/depois por anti-pattern
    └── testing-guidelines.md    # geração de testes por stack (pytest / jest+supertest)
```

As 5 áreas de conhecimento obrigatórias estão cobertas (análise, catálogo, template, guidelines MVC, playbook) — mais uma sexta (`testing-guidelines.md`) que adicionei para gerar testes na Fase 3.

### Catálogo de anti-patterns (15 + deprecated)

Selecionei os padrões pelos problemas reais encontrados na análise manual, com severidade distribuída:

- **CRITICAL:** Hardcoded Secrets · SQL Injection · God Class/Module · Senhas inseguras
- **HIGH:** Fat Controller · Estado global mutável · Ausência de camadas · Callback Hell
- **MEDIUM:** Queries N+1 · Erros genéricos/ausentes · Validação duplicada · Config hardcoded
- **LOW:** Magic numbers/strings · Nomenclatura ruim / código morto / print-log
- **Deprecated APIs (verificação obrigatória):** tabela com `datetime.utcnow()`, `Model.query.get()`, `@app.before_first_request`, `new Buffer()`, `sqlite3` callback API, `md5`/`sha1` para senhas etc., cada um com o equivalente moderno.

Cada item traz **sinais de detecção acionáveis** ("query SQL montada por concatenação", não "código ruim") para o agente conseguir apontar `arquivo:linha`.

### Como garanti o agnosticismo

- **Fase 1 detecta a stack** (linguagem, framework+versão, banco, ferramenta de teste) por manifestos e extensões — nada é presumido.
- O catálogo descreve anti-patterns em **termos conceituais** com exemplos em Python **e** Node, não regras amarradas a um framework.
- A Fase 3 **adapta-se ao contexto**: monolito → cria a estrutura MVC completa; projeto já em camadas → corrige violações **sem recriar** diretórios existentes.
- A validação é **comportamental** (boot + endpoints + testes), independente da linguagem.

### Desafios e como resolvi

- **Não recriar estrutura existente (projeto 3):** a regra "adapte-se ao contexto" no `execute.md` obriga o agente a decidir a estratégia **antes** de criar qualquer diretório.
- **Modificação sem aprovação:** o gate `[y/n]` (via `AskUserQuestion`) entre Fase 2 e 3 é uma regra inviolável — nenhum arquivo é tocado antes do `y`.
- **Verde artificial nos testes:** o `execute.md` proíbe relaxar testes para passar; falha → corrige o código refatorado.
- **Colisão de porta:** `code-smells-project` e `task-manager-api` usam a porta 5000 — a validação roda uma app por vez (e a config lê `PORT` do ambiente).

---

## C) Resultados

### Findings por severidade

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | Relatório |
|---|---|---|---|---|---|---|
| 1 — code-smells-project | 5 | 4 | 4 | 3 | **16** | [`audit-project-1.md`](reports/audit-project-1.md) |
| 2 — ecommerce-api-legacy | 3 | 4 | 5 | 1 | **13** | [`audit-project-2.md`](reports/audit-project-2.md) |
| 3 — task-manager-api | 2 | 2 | 5 | 2 | **11** | [`audit-project-3.md`](reports/audit-project-3.md) |

Todos superam o mínimo exigido (≥5 findings, ≥1 CRITICAL/HIGH).

### Antes → depois da estrutura

**Projeto 1 — monolito → MVC completo**
```
Antes:  app.py · controllers.py · models.py · database.py        (4 arquivos)
Depois: config/ · models/ (produto,usuario,pedido) · routes/ · controllers/
        · services/ · database/ (connection,schema) · middlewares/error_handler
        · utils/ · tests/ · app.py (application factory)
```

**Projeto 2 — God Class → camadas**
```
Antes:  src/app.js · src/AppManager.js · src/utils.js            (3 arquivos)
Depois: src/config/ · src/db/ (connection,schema) · src/models/ (course,user,
        enrollment,payment,auditLog,report) · src/services/ (checkout,report,
        user,password) · src/controllers/ · src/routes/ · src/middlewares/
        errorHandler · src/server.js · tests/
```

**Projeto 3 — camadas ilusórias → camadas reais** (estrutura existente preservada)
```
Antes:  lógica presa em routes/; services/ só com NotificationService (nunca usado)
Depois: routes/ finas → services/ (task,user,report,category,notification)
        + config/settings.py · middlewares/error_handler.py · tests/
        (models/ e utils/ mantidos e corrigidos, sem recriar diretórios)
```

### Validação (runtime) — todos os projetos **PASS**

| Projeto | Boot | Endpoints | Testes | Detalhe |
|---|---|---|---|---|
| 1 | ✓ sem erros | ✓ 8/8 → HTTP 200 | ✓ pytest | Porta 5001 (via `PORT`), `loja.db` auto-criado |
| 2 | ✓ sem erros | ✓ checkout/report/delete OK; recusa → 400 controlado | ✓ jest+supertest | Porta 3000, sqlite in-memory |
| 3 | ✓ sem erros | ✓ 11/11 → HTTP 200 | ✓ pytest 31 passed (`-W error::DeprecationWarning`) | Porta 5000, após `seed.py` |

Relatórios completos: [`reports/validation-project-{1,2,3}.md`](reports/).

### Checklist de validação (representativo — projeto 3)

```
Fase 1 — Análise
[x] Linguagem detectada (Python 3)   [x] Framework (Flask 3.0.0 + SQLAlchemy 3.1.1)
[x] Domínio (Task manager)           [x] Nº de arquivos condiz (15 .py)

Fase 2 — Auditoria
[x] Relatório segue o template       [x] Cada finding com arquivo:linha
[x] Ordenado por severidade          [x] ≥5 findings (11)
[x] Deprecated APIs (utcnow, Query.get, md5)   [x] Pausou e pediu confirmação [y/n]

Fase 3 — Refatoração
[x] Estrutura MVC (existente preservada + config/, middlewares/, tests/)
[x] Config sem hardcoded             [x] Models abstraem dados
[x] Routes só roteiam               [x] Services concentram o fluxo
[x] Error handling centralizado      [x] Entry point claro (create_app)
[x] App inicia sem erros             [x] Endpoints respondem (21 exercitados)
[x] Testes passam (pytest: 31 passed)
```

Os checklists dos projetos 1 e 2 estão nos respectivos relatórios de validação.

### Comportamento nas diferentes stacks

A mesma skill, a partir da raiz, cobriu Python/Flask+raw-sqlite (monolito), Node/Express (God Class assíncrona) e Python/Flask-SQLAlchemy (camadas parciais) — gerando ferramenta de teste idiomática por stack (`pytest` vs `jest+supertest`) e adaptando a estratégia de refatoração ao nível de decay de cada projeto.

---

## D) Como Executar

### Pré-requisitos

- **Claude Code** instalado e autenticado.
- **Python 3.10+** (projetos 1 e 3) e **Node.js 18+** (projeto 2).

### Executar a skill

A partir da **raiz do repositório**, passando o diretório-alvo como argumento:

```bash
claude "/refactor-arch code-smells-project"     # Projeto 1 — Python/Flask
claude "/refactor-arch ecommerce-api-legacy"    # Projeto 2 — Node/Express
claude "/refactor-arch task-manager-api"        # Projeto 3 — Python/Flask-SQLAlchemy
```

A skill executa Fase 1 (análise) → Fase 2 (auditoria + relatório em `reports/`) → **pausa e pede `[y/n]`** → Fase 3 (refatoração + testes + validação). Sem argumento, ela para e mostra o uso.

### Rodar os projetos já refatorados (para validar)

`code-smells-project` e `task-manager-api` usam a **porta 5000 — rode um por vez**.

```bash
# Projeto 1 — Flask + raw sqlite (auto-cria e popula loja.db no 1º boot)
cd code-smells-project && pip install -r requirements.txt && python app.py        # :5000
pytest                                                                            # testes

# Projeto 2 — Express + sqlite in-memory (auto-popula no boot; requisições em api.http)
cd ecommerce-api-legacy && npm install && npm start                               # :3000
npm test                                                                          # testes

# Projeto 3 — Flask-SQLAlchemy (SEED obrigatório antes do 1º boot)
cd task-manager-api && pip install -r requirements.txt && python seed.py && python app.py   # :5000
pytest                                                                            # testes
```

### Como validar que a refatoração funcionou

1. A aplicação **sobe sem erros** (`python app.py` / `npm start`).
2. **Todos os endpoints originais respondem** — teste com `curl` ou o arquivo `api.http` (projeto 2).
3. A **suíte de testes passa** (`pytest` / `npm test`).

---

## Estrutura do repositório

```
.
├── README.md                       # este documento (entregável)
├── CLAUDE.md                       # guia para o Claude Code neste repo
├── docs/CHALLENGE.md               # enunciado original do desafio
├── HISTORY.md                      # timeline de evolução do projeto
├── .claude/skills/refactor-arch/   # A SKILL (cópia única, invocada por argumento)
├── reports/                        # audit-project-{1,2,3}.md + validações
├── code-smells-project/            # Projeto 1 refatorado (Python/Flask)
├── ecommerce-api-legacy/           # Projeto 2 refatorado (Node/Express)
└── task-manager-api/               # Projeto 3 refatorado (Python/Flask-SQLAlchemy)
```

---

## Histórico

A evolução do projeto commit a commit está documentada em [`HISTORY.md`](HISTORY.md).
