================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python 3 + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 (SQLite)
Files:   15 analyzed | ~1,160 lines of code
Date:    2026-07-17

## Summary
CRITICAL: 2 | HIGH: 2 | MEDIUM: 5 | LOW: 2

## Findings

### [CRITICAL] Hardcoded Credentials / Secrets
File: app.py:13, services/notification_service.py:7-10
Description: `SECRET_KEY = 'super-secret-key-123'` embutida no código em `app.py:13`. `NotificationService` embute credenciais SMTP completas — host, porta, usuário `taskmanager@gmail.com` e senha `senha123` — em `services/notification_service.py:7-10`.
Impact: Qualquer pessoa com acesso ao repositório obtém a chave de assinatura de sessão do Flask e credenciais de e-mail. Rotação exige mudança de código e novo deploy.
Recommendation: Mover para variáveis de ambiente lidas por um módulo `config.py` (python-dotenv já está em requirements.txt e não é usado). Playbook: "Hardcoded secrets → config por ambiente".

### [CRITICAL] Armazenamento inseguro de senhas + senha exposta na API
File: models/user.py:29, models/user.py:32, models/user.py:21, routes/user_routes.py:85-86, routes/user_routes.py:129, routes/user_routes.py:209
Description: Senhas são hasheadas com MD5 sem salt (`hashlib.md5(pwd.encode()).hexdigest()` em `models/user.py:29` e comparação em `:32`). Pior: `User.to_dict()` serializa o campo `password` (`models/user.py:21`), e esse dict é devolvido diretamente nas respostas de POST /users (`user_routes.py:85-86`), PUT /users/<id> (`:129`), GET /users/<id> (`:33`) e POST /login (`:209`). O login ainda devolve um token falso `'fake-jwt-token-' + str(user.id)` (`user_routes.py:210`).
Impact: Hashes MD5 sem salt são quebráveis por rainbow table em segundos; a API entrega esses hashes a qualquer cliente. O token previsível permite personificação trivial.
Recommendation: Usar `werkzeug.security.generate_password_hash`/`check_password_hash`; remover `password` do `to_dict()`; emitir token real (JWT) ou remover a promessa de token. Playbook: "MD5 → werkzeug.security".

### [HIGH] Regra de negócio em Controller/Rota (Fat Controller)
File: routes/task_routes.py:11-63, routes/task_routes.py:85-154, routes/task_routes.py:273-299, routes/report_routes.py:12-101, routes/report_routes.py:103-155, routes/user_routes.py:42-90, routes/user_routes.py:134-151
Description: Handlers concentram validação, serialização manual campo a campo, cálculo de "overdue" e agregação de relatórios. O cálculo de atraso (`due_date < utcnow and status not in ...`) está copiado em 5 pontos: `task_routes.py:30-39`, `task_routes.py:71-80`, `task_routes.py:283-287`, `user_routes.py:171-180`, `report_routes.py:33-43` — enquanto `Task.is_overdue()` (`models/task.py:50-60`) existe e nunca é chamado. `report_routes.py:12-101` monta um relatório inteiro (90 linhas) dentro da rota. `user_routes.py:140-142` implementa cascade-delete manual de tasks na rota.
Impact: Impossível testar regra de negócio sem subir HTTP; qualquer mudança na regra de atraso exige editar 5 arquivos; alto risco de divergência (já há serialização inconsistente entre `get_tasks` e `to_dict`).
Recommendation: Extrair camada de services (`task_service.py`, `user_service.py`, `report_service.py`, `category_service.py`); rotas viram controllers finos que delegam. Playbook: "Fat controller → service layer".

### [HIGH] Ausência de disciplina de camadas / acoplamento direto ao ORM
File: routes/task_routes.py:14, routes/user_routes.py:12, routes/report_routes.py:15-28, services/notification_service.py:4-48, utils/helpers.py:57-108
Description: Todos os handlers consultam o ORM diretamente (`Task.query...`, `db.session...`) sem camada intermediária. A estrutura de camadas existe mas não é usada: `services/` contém apenas `NotificationService`, que nunca é importado por nenhuma rota (e mantém estado em memória `self.notifications`, `notification_service.py:6`); `utils/helpers.py` define `process_task_data` (`:57-108`), validadores e constantes (`:110-116`) que nenhuma rota usa — a validação foi reimplementada inline em cada handler.
Impact: A "arquitetura em camadas" é ilusória: toda a lógica real está nas rotas, o que anula testabilidade e reuso; código morto confunde manutenção.
Recommendation: Consolidar validação/serialização nos models e services; remover ou integrar `NotificationService` e `process_task_data`. Não recriar diretórios — corrigir a disciplina dentro da estrutura existente.

### [MEDIUM] Queries N+1
File: routes/task_routes.py:42, routes/task_routes.py:51, routes/report_routes.py:56, routes/report_routes.py:163
Description: GET /tasks executa `User.query.get(t.user_id)` e `Category.query.get(t.category_id)` dentro do loop sobre todas as tasks (`task_routes.py:41-57`) — 2N+1 queries. GET /reports/summary consulta as tasks de cada usuário uma a uma (`report_routes.py:55-61`). GET /categories faz um `count()` por categoria (`report_routes.py:163`).
Impact: Latência cresce linearmente com o volume de dados; com 1.000 tasks, a listagem dispara ~2.000 queries.
Recommendation: Usar `joinedload`/`selectinload` ou JOIN com agregação (`func.count` + `group_by`). Playbook: "N+1 → eager loading".

### [MEDIUM] Tratamento de erros ausente ou genérico
File: routes/task_routes.py:62-63, routes/task_routes.py:137, routes/task_routes.py:236, routes/user_routes.py:130, routes/user_routes.py:149, routes/report_routes.py:186, routes/report_routes.py:207, routes/report_routes.py:221, routes/report_routes.py:196
Description: `except:` bare engolindo qualquer exceção (incl. `KeyboardInterrupt`) em 8 handlers, sempre devolvendo mensagem genérica sem log estruturado. `get_tasks` envolve toda a rota num try/except bare (`task_routes.py:62`) mascarando bugs. `update_category` não valida body ausente (`report_routes.py:196` acessa `data` sem checar `None` → 500). Não há error handler centralizado no app.
Impact: Erros reais ficam invisíveis (nem stack trace), dificultando diagnóstico; payload vazio derruba endpoint com 500 em vez de 400.
Recommendation: Registrar `app.errorhandler` centralizado, capturar exceções específicas (`ValueError`, `IntegrityError`) e usar `logging`. Playbook: "bare except → error handler central".

### [MEDIUM] Validação duplicada e frouxa
File: routes/task_routes.py:110-114, routes/task_routes.py:166-184, routes/user_routes.py:61, routes/user_routes.py:64-65, routes/user_routes.py:106, models/task.py:38-48
Description: Validações de título/status/prioridade copiadas entre `create_task` e `update_task`; `Task.validate_status`/`validate_priority` (`models/task.py:38-48`) existem e nunca são chamados. Regex de e-mail frouxa (sem TLD, aceita `a@b`) duplicada em `user_routes.py:61` e `:106`. Senha mínima de 4 caracteres (`user_routes.py:64-65`). `priority` sem `int()` defensivo em `task_routes.py:113` (payload com string → 500).
Impact: Regras divergem entre create/update com o tempo; contas com senha "1234" (o próprio seed usa) e e-mails inválidos passam.
Recommendation: Centralizar validação em schemas (marshmallow já está em requirements.txt, não usado) ou nos services; senha mínima ≥ 8. Playbook: "validação inline → schema única".

### [MEDIUM] Configuração hardcoded (não-secreta)
File: app.py:11, app.py:34
Description: URI do banco fixa (`sqlite:///tasks.db`, `app.py:11`) e `app.run(debug=True, host='0.0.0.0', port=5000)` (`app.py:34`) — debug mode ligado e bind em todas as interfaces, hardcoded.
Impact: `debug=True` em produção expõe o werkzeug debugger (RCE); impossível trocar banco/porta sem editar código.
Recommendation: Módulo `config.py` com classes por ambiente lendo `os.environ` (python-dotenv já disponível). Playbook: "config hardcoded → config por ambiente".

### [MEDIUM] APIs Deprecated
File: models/task.py:15-16, models/task.py:52, models/user.py:14, models/category.py:11, utils/helpers.py:38, seed.py:66-74, routes/task_routes.py:31, routes/task_routes.py:72, routes/task_routes.py:215, routes/task_routes.py:285, routes/user_routes.py:172, routes/report_routes.py:35-45, routes/report_routes.py:71, routes/report_routes.py:133, routes/task_routes.py:42-51, routes/task_routes.py:67, routes/task_routes.py:117-122, routes/task_routes.py:158, routes/task_routes.py:188-195, routes/task_routes.py:227, routes/user_routes.py:29, routes/user_routes.py:94, routes/user_routes.py:136, routes/user_routes.py:155, routes/report_routes.py:105, routes/report_routes.py:192, routes/report_routes.py:214
Description: (1) `datetime.utcnow()` — deprecado no Python ≥ 3.12 — usado em 18+ pontos, inclusive como default de colunas. (2) `Model.query.get(id)` — API legacy do SQLAlchemy 2.x (emite `LegacyAPIWarning`) — usado em 16 handlers.
Impact: Warnings hoje, quebra em versões futuras; `utcnow()` retorna datetime naive, fonte de bugs de timezone.
Recommendation: `datetime.now(timezone.utc)` e `db.session.get(Model, id)`. Detalhes na seção "Deprecated APIs".

### [LOW] Código morto, imports não usados e print como log
File: app.py:7, routes/task_routes.py:7, routes/user_routes.py:6, routes/report_routes.py:7-8, utils/helpers.py:3-7, routes/task_routes.py:149, routes/task_routes.py:153, routes/task_routes.py:219, routes/task_routes.py:234, routes/user_routes.py:83, routes/user_routes.py:89, routes/user_routes.py:147, utils/helpers.py:36-41
Description: Imports mortos em todo arquivo (`os, sys, json` em `app.py:7`; `json, os, sys, time` em `task_routes.py:7`; `hashlib, json` em `user_routes.py:6`; `format_date, calculate_percentage` importados e nunca usados em `report_routes.py:7`; `os, json, sys, math, hashlib` em `helpers.py:3-7`). `print()` como mecanismo de log em 8+ pontos. Helpers nunca chamados (`generate_id`, `log_action`, `sanitize_string`, `is_valid_color`).
Impact: Ruído de manutenção; logs de produção perdidos (print sem nível/estrutura).
Recommendation: Remover imports/funções mortos; substituir `print` por `logging`.

### [LOW] Magic numbers / strings repetidas
File: routes/task_routes.py:110, routes/task_routes.py:177, routes/task_routes.py:113, routes/task_routes.py:182, routes/user_routes.py:71, routes/user_routes.py:120, utils/helpers.py:110-116
Description: Lista de status `['pending', 'in_progress', 'done', 'cancelled']` e de roles `['user', 'admin', 'manager']` repetidas inline em 4+ pontos; limites `1..5`, `3..200`, `4` mágicos — enquanto as constantes `VALID_STATUSES`, `VALID_ROLES`, `MAX_TITLE_LENGTH` etc. já existem em `utils/helpers.py:110-116` e não são usadas em lugar nenhum.
Impact: Adicionar um status exige caçar todas as cópias; risco de divergência silenciosa.
Recommendation: Usar as constantes existentes (ou enums) como fonte única.

## Deprecated APIs
- `datetime.utcnow()` → `datetime.now(timezone.utc)` — models/task.py:15, models/task.py:16, models/task.py:52, models/user.py:14, models/category.py:11, utils/helpers.py:38, seed.py:66-74, routes/task_routes.py:31, routes/task_routes.py:72, routes/task_routes.py:215, routes/task_routes.py:285, routes/user_routes.py:172, routes/report_routes.py:35, routes/report_routes.py:42, routes/report_routes.py:45, routes/report_routes.py:71, routes/report_routes.py:133 (deprecado no Python ≥ 3.12; retorna datetime naive)
- `Model.query.get(id)` → `db.session.get(Model, id)` — routes/task_routes.py:42, routes/task_routes.py:51, routes/task_routes.py:67, routes/task_routes.py:117, routes/task_routes.py:122, routes/task_routes.py:158, routes/task_routes.py:188, routes/task_routes.py:195, routes/task_routes.py:227, routes/user_routes.py:29, routes/user_routes.py:94, routes/user_routes.py:136, routes/user_routes.py:155, routes/report_routes.py:105, routes/report_routes.py:192, routes/report_routes.py:214 (API legacy do SQLAlchemy 2.x)
- `md5` para senhas → bcrypt / `werkzeug.security` — models/user.py:29, models/user.py:32 (coberto no finding CRITICAL de senhas)

================================
Total: 11 findings
================================

---

## Checklist de Validação (preenchido após a Fase 3)

### Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python 3)
- [x] Framework detectado corretamente (Flask 3.0.0 + Flask-SQLAlchemy 3.1.1)
- [x] Domínio da aplicação descrito corretamente (Task manager)
- [x] Número de arquivos analisados condiz com a realidade (15 arquivos .py)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (11 findings)
- [x] Detecção de APIs deprecated incluída (datetime.utcnow, Query.get, md5)
- [x] Skill pausou e pediu confirmação antes da Fase 3 (resposta: y)

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC (camadas existentes preservadas; adicionados config/, middlewares/ e tests/)
- [x] Configuração extraída para módulo de config (config/settings.py, tudo via env, sem hardcoded)
- [x] Models criados para abstrair dados (models/ já existia; regras de entidade consolidadas, is_overdue como fonte única)
- [x] Views/Routes separadas para roteamento (routes/ agora só mapeia rota → service)
- [x] Controllers concentram o fluxo da aplicação (services/task|user|report|category_service.py)
- [x] Error handling centralizado (middlewares/error_handler.py: ApiError + handlers 404/500)
- [x] Entry point claro (app.py com create_app() application factory)
- [x] Aplicação inicia sem erros (python seed.py && python app.py, porta 5000)
- [x] Endpoints originais respondem corretamente (21 endpoints exercitados via curl: 200/201/400/401/404 conforme contrato)
- [x] Testes unitários passam (pytest: 31 passed, incl. -W error::DeprecationWarning)
