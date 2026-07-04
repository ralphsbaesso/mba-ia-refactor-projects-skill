# Criar skill **refactor-arch**

Criar uma Claude Code Skill chamada `refactor-arch` (em `.claude/skills/refactor-arch/`, com `SKILL.md` — nomes fixos pelo spec) capaz de analisar, auditar e refatorar **qualquer** codebase para o padrão MVC, de forma agnóstica de tecnologia. Regras completas em `README.md`.

## Invocação

- A skill é executada a partir do **diretório root** do repositório e recebe como **argumento obrigatório** o diretório do sub-projeto alvo:

```bash
claude "/refactor-arch code-smells-project"
claude "/refactor-arch ecommerce-api-legacy"
claude "/refactor-arch task-manager-api"
```

- **Se o diretório não for informado, a skill deve parar imediatamente a execução**, exibindo mensagem de erro com instrução de uso e a lista de sub-projetos disponíveis — nenhuma fase deve rodar
- Se o diretório informado não existir, a skill também deve parar com erro
- Todas as fases (análise, auditoria e refatoração) atuam **somente** dentro do diretório do sub-projeto informado
- A skill deve ser invocada **somente pelo usuário** (invocação explícita via `/refactor-arch`) — o modelo não pode acioná-la automaticamente. No `SKILL.md`, usar `disable-model-invocation: true` no frontmatter

A skill é composta por duas partes, que juntas cobrem as 3 fases sequenciais exigidas pelo desafio:

- **refactor-arch/analyze** → Fase 1 (Análise) + Fase 2 (Auditoria)
- **refactor-arch/execute** → Fase 3 (Refatoração)

## Parte 1 — Análise (analyze)

Parte principal, responsável pelo diagnóstico. Não modifica nenhum arquivo.

### Fase 1 — Análise da codebase
- Detectar linguagem, framework (com versão), dependências e banco de dados
- Identificar o domínio da aplicação (ex.: e-commerce, LMS, task manager)
- Mapear a arquitetura atual (monolito, camadas parciais etc.) e contar arquivos analisados
- Imprimir um resumo padronizado (ver "Exemplo de Uso no CLI" do README)

### Fase 2 — Auditoria (relatório)
- Cruzar o código contra o catálogo de anti-patterns dos arquivos de referência
- Identificar anti-patterns e code smells, classificando por severidade (CRITICAL / HIGH / MEDIUM / LOW, conforme a escala do README) com **arquivo e linha exatos**
- Gerar relatório estruturado seguindo o template de referência, com findings ordenados por severidade e sumário de contagem
- Incluir detecção de **APIs deprecated**, recomendando o equivalente moderno
- **Obrigatório:** pausar e pedir confirmação `[y/n]` antes de qualquer modificação — a Fase 3 só roda após aprovação humana
- Salvar o relatório em `reports/audit-project-{1,2,3}.md`

## Parte 2 — Execução (execute)

Executa a refatoração a partir do relatório aprovado na Fase 2.

### Fase 3 — Refatoração + Validação
- Reestruturar para MVC: `config/` (sem valores hardcoded), `models/`, `views`/`routes`, `controllers/`, error handling centralizado e entry point claro (composition root)
- Adaptar-se ao contexto do projeto: em projetos já parcialmente organizados (ex.: `task-manager-api`), corrigir violações sem recriar estrutura existente
- **Obrigatório:** validar o resultado — a aplicação inicia sem erros e todos os endpoints originais continuam respondendo (curl / `api.http`)
- Preencher o checklist de validação do README para cada projeto

## Arquivos de referência (Markdown, obrigatórios)

Cobrir as 5 áreas de conhecimento:

1. **Análise de projeto** — heurísticas de detecção de linguagem, framework, banco e arquitetura
2. **Catálogo de anti-patterns** — mínimo **8** anti-patterns com sinais de detecção e severidade distribuída, incluindo APIs deprecated
3. **Template de relatório** — formato padronizado da auditoria (Fase 2)
4. **Guidelines de arquitetura** — regras do MVC alvo e responsabilidade de cada camada
5. **Playbook de refatoração** — mínimo **8** transformações com exemplos de código antes/depois

## Critérios de aceite (obrigatórios nos 3 projetos)

A skill vive no root do repositório e deve funcionar, via argumento de diretório, em `code-smells-project/` (Python/Flask, monolito), `ecommerce-api-legacy/` (Node/Express, God Class) e `task-manager-api/` (Python/Flask, parcialmente organizado):

- [ ] Skill para a execução com erro claro quando invocada sem diretório (ou com diretório inexistente)
- [ ] Fase 1 detecta a stack corretamente
- [ ] Fase 2 encontra ≥ 5 findings, com pelo menos 1 CRITICAL ou HIGH
- [ ] Fase 2 pausa e pede confirmação antes de tocar em qualquer arquivo
- [ ] Fase 3: aplicação funciona após a refatoração (boot + endpoints)

## Entregáveis

- Skill completa em `.claude/skills/refactor-arch/` no root do repositório, recebendo o sub-projeto como argumento
- Código refatorado dos 3 projetos commitado
- `reports/audit-project-{1,2,3}.md`
- `README.md` atualizado com as seções: Análise Manual, Construção da Skill, Resultados e Como Executar
