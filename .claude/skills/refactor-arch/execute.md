# Parte 2 — Execução da Refatoração (Fase 3)

> Pré-condição: relatório da Fase 2 aprovado pelo usuário (`y`). Fonte de verdade: o relatório salvo em `reports/` + [references/mvc-guidelines.md](references/mvc-guidelines.md) + [references/refactoring-playbook.md](references/refactoring-playbook.md). Atue somente dentro de `TARGET/`.

## Princípios

1. **Comportamento preservado**: todos os endpoints originais (método + path + formato de resposta) devem continuar respondendo. Refatoração muda estrutura, não contrato.
2. **Adaptação ao contexto** (decida ANTES de criar qualquer diretório):
   - **Monolito sem camadas** → criar a estrutura MVC completa das guidelines.
   - **Projeto parcialmente organizado** (já tem `models/`, `routes/`, `services/`...) → **não recriar estrutura existente**. Corrigir as violações do relatório: mover lógica de negócio das rotas para services/controllers, extrair config, centralizar error handling, corrigir segurança/performance/deprecated.
3. **Um finding por vez**: percorra o relatório em ordem de severidade e aplique a transformação correspondente do playbook.
4. Corrija também as **APIs deprecated** apontadas, substituindo pelo equivalente moderno.

## Alvo estrutural (para monolitos)

Conforme [references/mvc-guidelines.md](references/mvc-guidelines.md):

- `config/` — configuração via variáveis de ambiente, **sem valores hardcoded** (secrets, portas, paths de banco). Manter defaults sensatos para a app subir sem env configurado.
- `models/` — acesso a dados e regras da entidade (queries parametrizadas / ORM).
- `views/` ou `routes/` — apenas mapeamento rota → controller.
- `controllers/` — orquestram request → validação → model → resposta.
- `middlewares/` (ou equivalente) — **error handling centralizado**.
- Entry point claro (composition root): monta app, injeta config, registra rotas e error handler.

## Procedimento

1. Releia o relatório aprovado e monte um plano de transformações (playbook item a item).
2. Aplique as transformações.
3. Remova o código antigo substituído (não deixar arquivos mortos duplicando lógica).
4. Atualize manifestos se necessário (novas dependências só quando indispensável).

## Validação (OBRIGATÓRIA — a fase só termina aqui)

1. **Boot**: instale as dependências e inicie a aplicação conforme o mecanismo do projeto (`python app.py`, `npm start`, ...). Se houver script de seed, rode-o antes. A aplicação deve subir **sem erros nem warnings de deprecation introduzidos**.
2. **Endpoints**: exercite **todos os endpoints originais** com `curl` (ou o arquivo `api.http` se existir), incluindo casos de sucesso e de erro esperado (404/400). Compare com o contrato original.
3. Falhou? Corrija e repita. Não declare a fase concluída com validação pendente.
4. Encerre o servidor ao final.

## Saída padronizada

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios resultante>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

Preencha também o **checklist de validação** do README do desafio (Fases 1, 2 e 3) para o projeto refatorado.
