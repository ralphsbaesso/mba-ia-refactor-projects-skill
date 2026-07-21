# HISTORY.md

Evolução do projeto considerando apenas os commits do usuário **ralphsbaesso** (Ralph Baesso).

> Nota: o commit inicial do repositório (`6d1ce62`, boilerplate do desafio) foi feito por outro autor (PierryMedeiros) e serve apenas como ponto de partida — não faz parte desta linha do tempo.

---

## Linha do tempo

### 04/07/2026 — 10:05 · `3a25b83` — Documentação do repositório

**`docs: add CLAUDE.md with repo guidance for Claude Code`** *(branch `main`)*

Primeira contribuição de Ralph: criação do `CLAUDE.md` (49 linhas), documentando o repositório para uso com o Claude Code. O arquivo estabelece o entendimento base do projeto:

- Esclarece que o repositório é um **scaffold de desafio de curso**, e não uma aplicação — o entregável é a skill `refactor-arch`.
- Mapeia os três projetos legados alvo (`code-smells-project`, `ecommerce-api-legacy`, `task-manager-api`), seus stacks, estados de decadência e problemas plantados intencionalmente.
- Documenta como rodar cada projeto alvo (dependências, seeds, portas) e as convenções de trabalho (nome fixo da skill, cinco áreas de conhecimento obrigatórias, citações `file:line`, relatórios em `reports/`).

*Commit executado com suporte do modelo "Opus 4.8 (1M context)".*

---

### 04/07/2026 — 11:44 · `472da86` — Entrega da skill `refactor-arch`

**`feat(refactor-arch): add MVC refactoring skill with reference docs`** *(branch `challenge`)*

Entrega principal do desafio: criação da skill do Claude Code que analisa, audita e refatora qualquer codebase para MVC, de forma agnóstica de tecnologia. Foram 9 arquivos novos, **785 linhas adicionadas**:

| Arquivo | Papel |
|---|---|
| `.claude/skills/refactor-arch/SKILL.md` (72 linhas) | Ponto de entrada da skill, com o fluxo de 3 fases |
| `.claude/skills/refactor-arch/analyze.md` (61) | Instruções das Fases 1–2 (detectar stack, auditar) |
| `.claude/skills/refactor-arch/execute.md` (55) | Instruções da Fase 3 (refatorar + validar em runtime) |
| `references/project-analysis.md` (78) | Heurísticas de análise de projeto |
| `references/anti-patterns.md` (96) | Catálogo de anti-patterns (incl. detecção de APIs deprecadas) |
| `references/report-template.md` (42) | Template do relatório de auditoria |
| `references/mvc-guidelines.md` (58) | Diretrizes de arquitetura MVC |
| `references/refactoring-playbook.md` (245) | Playbook de refatoração com transformações antes/depois |
| `task.md` (78) | Especificação do desafio e critérios de aceite |

Pontos-chave do design implementado:

- **Fluxo em 3 fases sequenciais**: detecção de stack → auditoria com **gate de confirmação `[y/n]`** antes de tocar qualquer arquivo → refatoração com **validação em runtime** (app sobe e endpoints respondem).
- **Cobertura das cinco áreas de conhecimento obrigatórias** do spec via arquivos de referência em Markdown.
- Criação da branch **`challenge`** para abrigar a entrega, publicada no remoto.

*Commit executado com suporte do modelo "Fable 5 (200k context)".*

---

### 04/07/2026 — 16:40 · `a548719` — Início da linha do tempo

**`docs: add HISTORY.md with project evolution timeline`** *(branch `challenge`)*

Criação deste próprio arquivo `HISTORY.md` (56 linhas), documentando a evolução do projeto restrita aos commits de Ralph. Estabelece a convenção da linha do tempo — data/hora, hash, mensagem, branch e resumo por commit — usada daqui em diante.

*Commit executado com suporte do modelo "Fable 5 (200k context)".*

---

### 04/07/2026 — 16:55 · `aa15875` — Geração de testes unitários na Fase 3

**`feat(refactor-arch): generate unit tests in Phase 3`** *(branch `challenge`)*

Extensão da skill para que a Fase 3 também produza uma suíte de testes unitários das camadas refatoradas, complementando a validação de boot + endpoints. 4 arquivos, **198 inserções**:

- Novo `references/testing-guidelines.md` (179 linhas) cobrindo ferramentas por stack (pytest / jest+supertest), o que testar, manifesto e comando de execução.
- `execute.md`: geração de testes e suíte passando passam a ser exigidas na Fase 3.
- `analyze.md`: detecção da ferramenta de teste do stack já na Fase 1.
- `SKILL.md`: documenta o novo passo e a regra inviolável.

*Commit executado com suporte do modelo "Opus 4.8 (1M context)".*

---

### 15/07/2026 — 22:03 · `e7d182c` — Refatoração do Projeto 1 (`code-smells-project`)

**`refactor(code-smells): restructure monolith into MVC architecture`** *(branch `challenge`)*

Primeira aplicação real da skill sobre um alvo. O monólito Flask (`app.py`, `controllers.py`, `models.py`, `database.py`) foi quebrado em pacotes por camada: `config`, `controllers`, `models`, `routes`, `services`, `middlewares`, `utils` e `database`. 40 arquivos, **+1.238 / −768 linhas**:

- `SECRET_KEY` hardcoded movido para `config/settings.py`.
- Conexão global de DB substituída por conexão por requisição.
- Testes unitários de models, services e endpoints (Fase 3).
- Relatórios `reports/audit-project-1.md` e `reports/audit-result-1.md`.

*Commit executado com suporte do modelo "Fable 5 (200k context)".*

---

### 16/07/2026 — 22:22 · `f393db8` — Refatoração do Projeto 2 (`ecommerce-api-legacy`)

**`refactor(ecommerce): restructure AppManager monolith into MVC`** *(branch `challenge`)*

A God-class `AppManager.js` foi dividida em camadas `config`, `db`, `models`, `services`, `controllers`, `routes` e `middleware`. 31 arquivos, **+4.997 / −1.009 linhas** (grande parte em `package-lock.json`):

- Hashing de senha extraído para `passwordService`.
- Suítes de teste unitário e de endpoints (models, services, endpoints).
- Relatórios `reports/audit-project-2.md` e `reports/audit-result-2.md`.

---

### 17/07/2026 — 16:03 · `68de69a` — Refatoração do Projeto 3 (`task-manager-api`)

**`refactor(task-manager): fix layer violations and add service layer`** *(branch `challenge`)*

Alvo já parcialmente organizado: aqui "refatorar" foi corrigir violações, não criar estrutura. 27 arquivos, **+1.371 / −862 linhas**:

- Lógica de negócio extraída das `routes/` para `services/` (task, user, category, report).
- App factory com `config/settings.py`, removendo `SECRET_KEY` hardcoded e config inline.
- Tratamento de erros centralizado em `middlewares/error_handler.py`.
- Models e `utils/helpers` reduzidos às suas responsabilidades.
- Suíte pytest (models, services, endpoints) e relatórios `reports/audit-project-3.md` / `reports/audit-result-3.md`.

---

### 17/07/2026 — 20:47 · `dde6ded` — Validação em runtime dos três apps

**`docs(reports): add runtime validation reports for the three apps`** *(branch `challenge`)*

Evidência do critério de aceite da Fase 3 (app sobe + endpoints respondem). 3 arquivos, **140 inserções**:

- `validation-project-1.md`: code-smells (Flask) em `:5001`, 8/8 endpoints 200.
- `validation-project-2.md`: ecommerce (Express) em `:3000`, todos OK.
- `validation-project-3.md`: task-manager (Flask) em `:5000`, 11/11 endpoints 200.

Apps rodados em paralelo, em subagentes isolados; colisão da porta 5000 evitada via `PORT` (sem alterar código-fonte).

*Commit executado com suporte do modelo "Opus 4.8 (1M context)".*

---

### 17/07/2026 — 21:04 · `6b0740c` — README como entregável e skill única na raiz

**`docs: rewrite README as deliverable and drop per-project skill copies`** *(branch `challenge`)*

Consolidação final: em vez de copiar `.claude/skills` para dentro de cada projeto, adota-se uma **skill única na raiz** invocada com o diretório-alvo como argumento. 4 arquivos, **+648 / −456 linhas**:

- `README.md` reescrito com as seções exigidas do entregável: análise manual, construção da skill, resultados e como executar.
- Enunciado original do desafio movido para `docs/CHALLENGE.md`.
- `task.md` removido e `.pytest_cache/` adicionado ao `.gitignore`.

*Commit executado com suporte do modelo "Opus 4.8 (1M context)".*

---

### 21/07/2026 — 20:41 · `fc3b88b` — Skill copiada para dentro dos 3 projetos (feedback do avaliador)

**`refactor(skill): move refactor-arch into the three projects with cwd-based Step 0`** *(branch `challenge`)*

O avaliador rejeitou a abordagem de cópia única na raiz: o entregável exige a skill **dentro** de `code-smells-project`, `ecommerce-api-legacy` e `task-manager-api`. 29 arquivos, **+1829 / −41 linhas**:

- `.claude/skills/refactor-arch/` replicada (cópias idênticas) em `<projeto>/.claude/skills/refactor-arch/` nos três projetos; cópia da raiz removida.
- **Passo 0 reescrito**: `TARGET = diretório corrente` (sem argumento) — valida que o cwd parece a raiz de um projeto (manifesto ou entrypoint) e, fora de um projeto, para com instrução de uso. Relatório vai para `REPORTS_DIR` (raiz do repo git → `reports/`; fallback `./reports/`).
- Invocação passa a ser `cd <projeto> && claude "/refactor-arch"`. `README.md` (abordagem de invocação, como executar, árvore do repo) e `CLAUDE.md` atualizados.
- Smoke test em cópia isolada: Fases 1–2 rodam de dentro do projeto sem argumento e param no gate `[y/n]`; guard do Passo 0 barra diretório não-projeto.

*Commit executado com suporte do modelo "Fable 5".*

---

## Resumo da evolução

1. **Fundação de contexto** (`main`): antes de escrever código, Ralph documentou o repositório em `CLAUDE.md`, fixando o entendimento do desafio, dos projetos alvo e das regras de validação.
2. **Entrega da skill** (`challenge`): ~1h40 depois, entregou a skill `refactor-arch` completa — entrypoint, instruções por fase e as cinco referências exigidas — cumprindo os requisitos duros do spec (gate de confirmação na Fase 2 e validação comportamental na Fase 3).
3. **Testes na Fase 3** (`challenge`): a skill foi estendida para gerar suítes de teste unitário além da validação comportamental, com um novo arquivo de referência de testing.
4. **Aplicação nos três alvos** (`challenge`): ao longo de 15–17/07, a skill foi aplicada aos três projetos legados — monólito Flask, God-class Express e API já parcialmente organizada —, cada um com sua auditoria e refatoração para MVC, adaptando-se ao nível de decadência de cada codebase.
5. **Fechamento** (`challenge`): validação em runtime dos três apps evidenciando o critério de aceite, seguida da reescrita do `README` como entregável e da adoção de uma skill única na raiz.
6. **Reenvio** (`challenge`): após feedback do avaliador, a skill foi copiada para dentro dos três projetos (cópias idênticas) com o Passo 0 reescrito para operar sobre o diretório corrente, sem argumento — estado final do entregável.
