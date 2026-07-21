---
name: refactor-arch
description: Analisa, audita e refatora qualquer codebase para o padrão MVC (agnóstico de tecnologia). Executada de dentro do projeto-alvo (diretório corrente), sem argumentos. Executa 3 fases sequenciais - análise, auditoria com relatório e refatoração validada.
disable-model-invocation: true
---

# refactor-arch — Refatoração Arquitetural Automatizada

Skill agnóstica de tecnologia que analisa, audita e refatora um sub-projeto para o padrão MVC em 3 fases sequenciais. É composta por duas partes:

- **Parte 1 — Análise** (`analyze.md`): Fase 1 (análise da codebase) + Fase 2 (auditoria e relatório). **Não modifica nenhum arquivo.**
- **Parte 2 — Execução** (`execute.md`): Fase 3 (refatoração MVC + validação de runtime). Só roda após aprovação humana explícita.

## Passo 0 — Validação do diretório de execução (OBRIGATÓRIO, antes de qualquer fase)

A skill é executada **de dentro do projeto-alvo**: o alvo é sempre o diretório corrente. Ela não recebe nem depende de argumento.

1. **Defina `TARGET = diretório corrente (.)`** — o diretório onde o Claude Code foi iniciado.

2. **Valide que `TARGET` parece a raiz de um projeto**: deve conter um manifesto de dependências (`requirements.txt`, `pyproject.toml`, `package.json`, `go.mod`, `pom.xml`, `Gemfile`, `composer.json`, …) **ou** um entrypoint óbvio de aplicação (`app.py`, `main.py`, `src/app.js`, `index.js`, …). A lista é ilustrativa — use o equivalente da stack encontrada.

3. **Se `TARGET` NÃO parecer um projeto** (ex.: é a raiz de um repositório que apenas contém sub-projetos): **PARE IMEDIATAMENTE**. Não execute nenhuma fase, não leia nenhum arquivo de projeto. Exiba esta mensagem de erro (listando como candidatos os subdiretórios que não começam com `.` e não são `reports/`) e encerre:

   ```
   ERRO: o diretório corrente não parece a raiz de um projeto
   (nenhum manifesto de dependências ou entrypoint encontrado).

   Entre no projeto-alvo e invoque a skill de lá:

     cd <projeto>
     claude "/refactor-arch"

   Projetos candidatos encontrados: <lista>
   ```

4. **Defina o destino do relatório**: `REPORTS_DIR = <raiz do repositório git>/reports/` (use `git rev-parse --show-toplevel`). Se `TARGET` não estiver dentro de um repositório git, use `REPORTS_DIR = ./reports/` no próprio projeto. Crie o diretório se não existir.

5. **Todas as fases (análise, auditoria e refatoração) atuam SOMENTE dentro de `TARGET/`.** Nunca leia código nem modifique arquivos de projetos irmãos. A única escrita fora de `TARGET/` permitida é o relatório em `REPORTS_DIR`.

## Fluxo das fases

1. **Fases 1 e 2** — siga rigorosamente as instruções de [analyze.md](analyze.md). Ao final da Fase 2:
   - Salve o relatório em `REPORTS_DIR/audit-project-{N}.md` (N: 1 = code-smells-project, 2 = ecommerce-api-legacy, 3 = task-manager-api; outros projetos: use o nome do diretório).
   - **PAUSE OBRIGATORIAMENTE** e pergunte ao usuário: `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` usando a ferramenta AskUserQuestion. **Nenhum arquivo pode ser modificado antes da resposta.**
   - Resposta `n` → encerre a skill agradecendo, sem tocar em nada.
   - Resposta `y` → prossiga para a Fase 3.
2. **Fase 3** — siga rigorosamente as instruções de [execute.md](execute.md), usando o relatório aprovado como fonte dos problemas a corrigir. Além de reestruturar para MVC, **gere testes unitários** para as camadas produzidas (models e services/controllers) com a ferramenta adequada à stack. A fase termina somente após a validação de runtime (boot + todos os endpoints originais respondendo + suíte de testes passando).

## Arquivos de referência (conhecimento de domínio)

Consulte-os nas fases indicadas:

| Arquivo | Área de conhecimento | Usado em |
|---|---|---|
| [references/project-analysis.md](references/project-analysis.md) | Heurísticas de detecção de linguagem, framework, banco e arquitetura | Fase 1 |
| [references/anti-patterns.md](references/anti-patterns.md) | Catálogo de anti-patterns (sinais de detecção + severidade + APIs deprecated) | Fase 2 |
| [references/report-template.md](references/report-template.md) | Template padronizado do relatório de auditoria | Fase 2 |
| [references/mvc-guidelines.md](references/mvc-guidelines.md) | Regras do MVC alvo e responsabilidades de cada camada | Fase 3 |
| [references/refactoring-playbook.md](references/refactoring-playbook.md) | Transformações concretas antes/depois por anti-pattern | Fase 3 |
| [references/testing-guidelines.md](references/testing-guidelines.md) | Geração de testes unitários por stack (pytest / jest+supertest), o que cobrir, manifesto e execução | Fase 3 |

## Regras invioláveis

- Nunca pule o Passo 0.
- Fases 1 e 2 são somente leitura (exceto salvar o relatório em `REPORTS_DIR`).
- A confirmação `[y/n]` entre a Fase 2 e a Fase 3 é obrigatória — modificação sem aprovação humana é uma violação da skill.
- A Fase 3 só está completa quando a aplicação sobe sem erros, todos os endpoints originais respondem **e a suíte de testes unitários gerada passa** (`pytest` / `npm test`). Os testes complementam, não substituem, a validação de boot + endpoints.
- Adapte-se ao contexto: em projeto já parcialmente organizado, corrija violações sem recriar estrutura existente.
