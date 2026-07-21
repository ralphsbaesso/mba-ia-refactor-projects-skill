# Parte 1 — Análise e Auditoria (Fases 1 e 2)

> Pré-condição: `TARGET` validado pelo Passo 0 do SKILL.md. Esta parte **não modifica nenhum arquivo** — a única escrita permitida é o relatório em `reports/`.

## Fase 1 — Análise da codebase

Use as heurísticas de [references/project-analysis.md](references/project-analysis.md). Trabalhe somente dentro de `TARGET/`.

1. **Inventário**: liste os arquivos de código-fonte de `TARGET/` (ignore `node_modules/`, `venv/`, `__pycache__/`, `.git/`, artefatos de banco `.db`). Conte-os e leia todos (projetos-alvo são pequenos; se >50 arquivos, priorize entry points, rotas, models e config).
2. **Detecte a stack**:
   - Linguagem (por extensões e manifestos)
   - Framework **com versão exata** (leia `requirements.txt`, `package.json`, `pyproject.toml`, `go.mod`, etc.)
   - Dependências relevantes
   - Banco de dados (driver/ORM e tabelas — leia os `CREATE TABLE`/models)
   - **Ferramenta de teste** idiomática da stack, que a Fase 3 usará para gerar os testes (Python/Flask → `pytest`; Node/Express → `jest`/`vitest` + `supertest`). Note se já há testes ou runner configurado no manifesto.
3. **Identifique o domínio** da aplicação pelos nomes de tabelas, rotas e entidades (ex.: e-commerce, LMS, task manager).
4. **Mapeie a arquitetura atual**: monolito em poucos arquivos? God class? Camadas parciais (`models/`, `routes/`, `services/`)? Onde vivem rotas, regra de negócio, acesso a dados e configuração?
5. **Imprima o resumo padronizado** exatamente neste formato:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão>
Dependencies:  <deps relevantes>
Domain:        <domínio da aplicação>
Architecture:  <descrição curta da arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <tabelas>
================================
```

## Fase 2 — Auditoria

Cruze o código de `TARGET/` contra o catálogo [references/anti-patterns.md](references/anti-patterns.md), item por item.

Regras dos findings:

- Cada finding **deve** citar arquivo e linha(s) exatos (`arquivo.py:28` ou `arquivo.py:28-45`). Confira os números de linha lendo o arquivo — nunca estime.
- Classifique pela escala CRITICAL / HIGH / MEDIUM / LOW definida no catálogo.
- Inclua a verificação de **APIs deprecated** (seção própria do catálogo): identifique APIs obsoletas e recomende o equivalente moderno. Se nada for encontrado, registre "Nenhuma API deprecated detectada" no relatório.
- Ordene os findings por severidade (CRITICAL → HIGH → MEDIUM → LOW) e inclua o sumário de contagem.
- Mínimo esperado: 5 findings com pelo menos 1 CRITICAL ou HIGH. Se encontrar menos, releia o código — os projetos-alvo têm problemas plantados intencionalmente.

Gere o relatório seguindo **exatamente** o template de [references/report-template.md](references/report-template.md) e:

1. Imprima o relatório no chat.
2. Salve-o em `reports/audit-project-{N}.md` (crie `reports/` se não existir).

## Gate de confirmação (OBRIGATÓRIO)

Ao final da Fase 2, pergunte via AskUserQuestion:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

- **`n`** → encerre sem modificar nada.
- **`y`** → prossiga para a Parte 2 ([execute.md](execute.md)).

Nenhum arquivo de `TARGET/` pode ser tocado antes da resposta afirmativa.
