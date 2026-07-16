```bash
  ================================
  PHASE 3: REFACTORING COMPLETE
  ================================
  ## New Project Structure
  code-smells-project/
  ├── app.py                      # composition root: create_app() factory
  ├── config/
  │   ├── __init__.py
  │   └── settings.py             # config via env vars, sem secrets hardcoded
  ├── database/
  │   ├── __init__.py
  │   ├── connection.py           # conexão por request (Flask g) + teardown
  │   └── schema.py               # init_db idempotente + seed com senha hasheada
  ├── models/                     # acesso a dados parametrizado, sem HTTP
  │   ├── produto.py
  │   ├── usuario.py              # to_public_dict nunca serializa senha
  │   └── pedido.py               # leitura via JOIN (sem N+1) + agregação
  ├── services/                   # regra de negócio cross-entidade
  │   ├── pedido_service.py       # checagem de estoque, total, baixa
  │   └── relatorio_service.py    # faixas de desconto
  ├── controllers/                # orquestração request→model→resposta
  │   ├── produto_controller.py
  │   ├── usuario_controller.py   # hash + check_password_hash
  │   ├── pedido_controller.py
  │   ├── relatorio_controller.py
  │   └── health_controller.py
  ├── routes/                     # blueprints: só mapeamento rota→controller
  │   ├── produto_routes.py, usuario_routes.py, pedido_routes.py,
  │   └── relatorio_routes.py, main_routes.py
  ├── middlewares/
  │   └── error_handler.py        # ApiError + handlers centralizados (não vaza str(e))
  ├── utils/
  │   ├── constants.py            # categorias, status, faixas de desconto
  │   └── validators.py           # validação centralizada (DRY)
  ├── tests/
  │   ├── conftest.py             # app factory + DB temporário isolado
  │   ├── test_models.py          # serialização segura, anti-injection, JOIN
  │   ├── test_services.py        # estoque/total, desconto, erros de domínio
  │   └── test_endpoints.py       # regressão de contrato + regressões de segurança
  └── requirements.txt            # + pytest

  ## Validation
    ✓ Application boots without errors        (python app.py → :5000, sem deprecation warnings)
    ✓ All endpoints respond correctly         (16 endpoints originais: sucesso + 400/401/404 esperados)
    ✓ Unit tests pass (pytest: 19 passed)     — comando: pytest
    ✓ Zero anti-patterns remaining            (findings CRITICAL/HIGH/MEDIUM/LOW corrigidos)
  ================================

  Checklist do desafio:
    
  - Fase 1 ✓ — stack detectada (Python + Flask 3.1.1, SQLite bruto), domínio e-commerce, arquitetura monolítica mapeada, 4 arquivos-fonte, tabelas identificadas.
  - Fase 2 ✓ — 16 findings (5 CRITICAL, 4 HIGH, 4 MEDIUM, 3 LOW) com file:line exatos, relatório em reports/audit-project-1.md, gate [y/n] respeitado.
  - Fase 3 ✓ — MVC completo, testes gerados, boot + endpoints + pytest verdes.

  ## Validation
    ✓ Application boots without errors        (python app.py → :5000, sem deprecation warnings)
    ✓ All endpoints respond correctly         (16 endpoints originais: sucesso + 400/401/404 esperados)
    ✓ Unit tests pass (pytest: 19 passed)     — comando: pytest
    ✓ Zero anti-patterns remaining            (findings CRITICAL/HIGH/MEDIUM/LOW corrigidos)
  ================================

  Checklist do desafio:

  - Fase 1 ✓ — stack detectada (Python + Flask 3.1.1, SQLite bruto), domínio e-commerce, arquitetura monolítica mapeada, 4 arquivos-fonte, tabelas identificadas.
  - Fase 2 ✓ — 16 findings (5 CRITICAL, 4 HIGH, 4 MEDIUM, 3 LOW) com file:line exatos, relatório em reports/audit-project-1.md, gate [y/n] respeitado.
  - Fase 3 ✓ — MVC completo, testes gerados, boot + endpoints + pytest verdes.

  Como cada finding foi resolvido:

  ┌─────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────┐
  │                     Finding                     │                                 Correção                                 │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ Secrets hardcoded / ecoado no /health           │ config/settings.py lê de env; /health não devolve mais secret/debug      │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ SQL Injection (todas as queries)                │ placeholders ? em toda a camada model; search monta cláusulas com params │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ /admin/query (SQL arbitrário) + /admin/reset-db │ endpoints removidos                                                      │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ God Module models.py                            │ quebrado em models/ por entidade + services/ para regra cross-entidade   │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ Senhas em texto plano                           │ generate_password_hash/check_password_hash; senha nunca serializada      │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ Fat Controller                                  │ validação → utils/validators.py, regra → services/, controllers finos    │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ Conexão global mutável                          │ conexão por request via g + teardown_appcontext                          │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ Sem camadas / rotas manuais                     │ blueprints por domínio + create_app() factory                            │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ try/except vazando str(e)                       │ ApiError + handlers centralizados; str(e) só no log                      │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ N+1 em pedidos                                  │ JOIN único + agregação por CASE WHEN                                     │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ Validação duplicada                             │ validators reutilizáveis                                                 │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ Config hardcoded / schema acoplado a get_db     │ config/ por env; init_db separado                                        │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ print como log                                  │ app.logger                                                               │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ Magic numbers/strings                           │ utils/constants.py                                                       │
  ├─────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ id sombreando builtin / import morto            │ parâmetros nomeados, imports limpos                                      │
  └─────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────┘

  Deprecated APIs: nenhuma no legado; a refatoração também não introduziu nenhuma.
```
