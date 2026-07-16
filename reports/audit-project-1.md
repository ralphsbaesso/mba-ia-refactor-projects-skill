================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1 (flask-cors 5.0.1), SQLite via driver bruto (sqlite3)
Files:   4 analyzed | ~784 lines of code
Date:    2026-07-15

## Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 4 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Credentials / Secrets (catálogo #1)
File: app.py:7, controllers.py:289, database.py:76-78
Description: `SECRET_KEY` literal (`"minha-chave-super-secreta-123"`) embutido em `app.py:7`. Pior: o endpoint `/health` devolve esse mesmo secret no JSON de resposta (`controllers.py:289`). O seed grava senhas em texto plano no banco (`database.py:76-78`).
Impact: Secret exposto no VCS e ecoado por endpoint público permite forjar sessões/tokens; qualquer um que chame `/health` obtém a chave. Credenciais comprometidas de forma irreversível.
Recommendation: Mover `SECRET_KEY` para variável de ambiente lida por um módulo `config/`; remover o campo `secret_key` (e `debug`) da resposta de `/health`. Ver playbook "Secrets fora do código".

### [CRITICAL] SQL Injection por concatenação de strings (catálogo #2)
File: models.py:28, models.py:47-50, models.py:57-61, models.py:68, models.py:92, models.py:109-111, models.py:126-129, models.py:140, models.py:148-166, models.py:174, models.py:188, models.py:192, models.py:220, models.py:224, models.py:279-281, models.py:289-297
Description: Praticamente todas as queries são montadas concatenando input do usuário diretamente no SQL — incluindo `login_usuario` (`models.py:109-111`), a busca com `LIKE '%" + termo + "%'` (`models.py:291`) e todos os INSERT/UPDATE/DELETE. Nenhum placeholder (`?`) é usado no caminho de request.
Impact: Injeção de SQL trivial em todos os endpoints; bypass de autenticação no `/login`, leitura/escrita/exclusão arbitrária de dados.
Recommendation: Substituir toda concatenação por queries parametrizadas com placeholders `?` na camada de repositório. Ver playbook "Query parametrizada".

### [CRITICAL] Endpoint executa SQL arbitrário do request (catálogo #2)
File: app.py:59-78
Description: `/admin/query` recebe `sql` do corpo da requisição e o executa diretamente no banco, sem autenticação nem restrição.
Impact: RCE-equivalente sobre o banco — qualquer cliente lê e altera qualquer tabela. Também há `/admin/reset-db` (app.py:47-57) que apaga todas as tabelas sem auth.
Recommendation: Remover ambos os endpoints administrativos; se necessário, substituir por operações específicas protegidas por autenticação/autorização.

### [CRITICAL] God Module concentrando SQL de 4 domínios (catálogo #3)
File: models.py:1-315
Description: `models.py` reúne acesso a dados de produtos, usuários, pedidos/itens e relatórios num único módulo, misturando SQL, regra de negócio (cálculo de total/estoque em `criar_pedido`, faixas de desconto em `relatorio_vendas`) e montagem de dicionários de resposta.
Impact: Impossível testar ou evoluir camadas isoladamente; alto acoplamento; qualquer mudança afeta múltiplos domínios.
Recommendation: Quebrar em repositórios por entidade (Produto, Usuário, Pedido) na camada Model e mover regra de negócio para Services. Ver playbook "Quebra de God Module".

### [CRITICAL] Armazenamento inseguro de senhas (catálogo #4)
File: database.py:75-83, models.py:109-111, models.py:126-131, models.py:83, models.py:99
Description: Senhas são gravadas e comparadas em texto plano. Seed insere `"admin123"`, `"123456"`, `"senha123"` (`database.py:76-78`); `criar_usuario` grava a senha crua (`models.py:126-131`); `login_usuario` compara `senha == input` via SQL (`models.py:109-111`); a senha é serializada em respostas de listagem/detalhe de usuário (`models.py:83`, `models.py:99`).
Impact: Vazamento total de credenciais em caso de dump do banco; senhas expostas em respostas de API.
Recommendation: Fazer hash com `werkzeug.security.generate_password_hash`/`check_password_hash`; nunca serializar `senha`. Ver playbook "Hash de senha".

### [HIGH] Regra de negócio no Controller (Fat Controller) (catálogo #5)
File: controllers.py:24-62, controllers.py:64-96, controllers.py:188-220, controllers.py:237-255
Description: Handlers HTTP acumulam validação extensa (faixas de preço/estoque, tamanho de nome, lista de categorias em `criar_produto`), regras de negócio e efeitos colaterais simulados por `print` ("ENVIANDO EMAIL/SMS/PUSH" em `controllers.py:208-210`, notificações de status em `controllers.py:247-250`). Validação duplicada entre `criar_produto` e `atualizar_produto`.
Impact: Lógica não reutilizável nem testável fora do ciclo HTTP; duplicação; responsabilidades misturadas.
Recommendation: Mover validação e regras para camada Service; controllers só orquestram request/response. Ver playbook "Fat Controller → Service".

### [HIGH] Estado global mutável para conexão de DB (catálogo #6)
File: database.py:4, database.py:7-10
Description: Conexão única guardada em variável global de módulo (`db_connection`) e aberta com `check_same_thread=False`, compartilhada entre todas as threads do Flask.
Impact: Condições de corrida e corrupção de cursores sob concorrência; impossível isolar conexões em testes.
Recommendation: Usar conexão por request (padrão `g` do Flask / factory) ou pool, fechando ao fim do request. Ver playbook "Conexão por request".

### [HIGH] Ausência de camadas / roteamento manual no entry point (catálogo #7)
File: app.py:11-30, controllers.py:2-3, controllers.py:266
Description: Rotas registradas uma a uma via `app.add_url_rule` no entry point; controllers importam e chamam `get_db()`/models diretamente sem injeção de dependência; `health_check` acessa o DB diretamente (`controllers.py:266`).
Impact: Sem separação MVC real; entry point acoplado a cada handler; difícil manter e testar.
Recommendation: Introduzir Blueprints por domínio e camada de serviço/repositório; entry point vira factory `create_app()`. Ver playbook "Blueprints + factory".

### [HIGH] Tratamento de erros genérico vazando internals (catálogo #10)
File: controllers.py:10-12, controllers.py:21-22, controllers.py:60-62, controllers.py:95-96 (e demais handlers)
Description: Cada handler repete `try/except Exception as e` devolvendo `str(e)` ao cliente. O padrão está copiado em ~15 handlers.
Impact: Vazamento de detalhes internos (mensagens de SQL, stack) ao cliente; duplicação massiva; sem tratamento centralizado.
Recommendation: Error handler centralizado (`@app.errorhandler`) e exceções de domínio; remover try/except repetido. Ver playbook "Error handler central".

### [MEDIUM] Queries N+1 na montagem de pedidos (catálogo #9)
File: models.py:187-199, models.py:219-231
Description: `get_pedidos_usuario` e `get_todos_pedidos` abrem uma query por pedido para itens e mais uma query por item para o nome do produto (loops aninhados de queries).
Impact: Explosão de queries com o crescimento de pedidos/itens; latência alta.
Recommendation: Substituir por JOIN único entre pedidos, itens_pedido e produtos. Ver playbook "N+1 → JOIN".

### [MEDIUM] Validação ausente ou duplicada (catálogo #11)
File: controllers.py:30-54, controllers.py:74-90, controllers.py:157-158, controllers.py:170-174
Description: A mesma sequência de `if` de validação de produto está duplicada em criar/atualizar; criação de usuário só checa presença (sem formato de e-mail nem força de senha).
Impact: Regras inconsistentes e difíceis de manter; dados fracos aceitos.
Recommendation: Centralizar validação em funções/serviço reutilizável; validar formato de e-mail e senha mínima. Ver playbook "Validação centralizada".

### [MEDIUM] Configuração hardcoded não-secreta (catálogo #12)
File: app.py:8, app.py:88, database.py:5
Description: `DEBUG=True` (app.py:8 e app.py:88), host/porta fixos (`0.0.0.0:5000`) e `db_path = "loja.db"` embutidos no módulo.
Impact: Sem separação de ambientes; debug ligado em produção expõe o debugger interativo do Werkzeug.
Recommendation: Módulo `config/` lendo variáveis de ambiente com defaults. Ver playbook "Config por ambiente".

### [MEDIUM] Schema e seed acoplados à obtenção da conexão (catálogo #3/#12)
File: database.py:7-86
Description: `get_db()` cria as tabelas e semeia dados como efeito colateral de obter a conexão, misturando responsabilidade de infra/migração com acesso a dados.
Impact: Efeitos colaterais imprevisíveis; impossível obter conexão "limpa" em teste; seed roda implicitamente.
Recommendation: Separar `init_db()`/migração e `seed()` da obtenção da conexão. Ver playbook "Init/seed separados".

### [LOW] print() como mecanismo de log (catálogo #14)
File: controllers.py:8, controllers.py:11, controllers.py:57, controllers.py:61, controllers.py:106, controllers.py:161, controllers.py:179, controllers.py:182, controllers.py:208-210, controllers.py:219, controllers.py:248-250, app.py:56, app.py:83-86, database.py (boot)
Description: Uso disseminado de `print()` para logging e para simular efeitos colaterais de negócio.
Impact: Sem níveis de log, sem estrutura, poluição de stdout; efeitos de negócio não implementados de fato.
Recommendation: Usar o módulo `logging`; efeitos colaterais reais pertencem a serviços dedicados.

### [LOW] Magic numbers / strings (catálogo #13)
File: models.py:256-262, controllers.py:52, controllers.py:242, models.py:47-49
Description: Faixas de desconto (`> 10000 → 0.1`, `> 5000 → 0.05`, `> 1000 → 0.02`) sem constantes nomeadas; listas de categorias/status válidos repetidas inline em pontos diferentes.
Impact: Regras difíceis de localizar e manter; risco de divergência entre cópias.
Recommendation: Extrair para constantes/enums nomeados na camada apropriada.

### [LOW] Sombreamento de builtin e import não usado (catálogo #14)
File: models.py:24, models.py:2, controllers.py:14
Description: Parâmetro `id` sombreia o builtin em várias funções (`get_produto_por_id`, `buscar_produto`, etc.); `import sqlite3` em `models.py:2` não é usado.
Impact: Legibilidade e risco de bugs sutis; código morto.
Recommendation: Renomear `id` para `produto_id`/`usuario_id`; remover import morto.

## Deprecated APIs
Nenhuma API deprecated detectada. Não há uso de `datetime.utcnow()`, `@app.before_first_request`, `Query.get()` legado nem drivers obsoletos; os timestamps são gerados pelo SQLite (`CURRENT_TIMESTAMP`). Flask 3.1.1 e flask-cors 5.0.1 estão atualizados.

================================
Total: 16 findings
================================
