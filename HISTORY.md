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

## Resumo da evolução

1. **Fundação de contexto** (`main`): antes de escrever código, Ralph documentou o repositório em `CLAUDE.md`, fixando o entendimento do desafio, dos projetos alvo e das regras de validação.
2. **Entrega da skill** (`challenge`): ~1h40 depois, entregou a skill `refactor-arch` completa — entrypoint, instruções por fase e as cinco referências exigidas — cumprindo os requisitos duros do spec (gate de confirmação na Fase 2 e validação comportamental na Fase 3).
