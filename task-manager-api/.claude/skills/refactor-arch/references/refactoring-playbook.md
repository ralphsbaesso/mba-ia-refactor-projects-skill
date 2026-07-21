# Playbook de Refatoração

Transformações concretas por anti-pattern, com antes/depois. Aplicar na ordem do relatório (CRITICAL primeiro). Regra de ouro: **o contrato dos endpoints não muda**.

## T1 — Extrair configuração hardcoded para módulo de config (env)

**Antes** (`app.py`):
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
app.run(host="0.0.0.0", port=5000, debug=True)
```

**Depois** (`config/settings.py` + composition root):
```python
# config/settings.py
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    PORT = int(os.environ.get("PORT", "5000"))

# app.py
app.config.from_object(Config)
app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
```
Equivalente Node: `config/index.js` lendo `process.env.PORT || 3000`, `process.env.PAYMENT_GATEWAY_KEY`, etc.

## T2 — Eliminar SQL Injection: concatenação → query parametrizada

**Antes**:
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
```

**Depois**:
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))  # senha comparada via hash, nunca no SQL
```
Filtros dinâmicos: montar lista de cláusulas + lista de parâmetros; nunca interpolar valores (`nome LIKE ?` com `f"%{termo}%"` como parâmetro).

## T3 — Explodir God Class/Module em camadas

**Antes** (`AppManager.js`): uma classe cria o banco, define schema, registra rotas e processa checkout.

**Depois**:
```
src/
├── app.js                    # composition root: monta express, injeta db, registra rotas
├── config/index.js
├── db/connection.js          # abre conexão + promisifica run/get/all
├── db/schema.js              # CREATE TABLEs + seed
├── models/courseModel.js     # findActiveById(db, id)...
├── models/userModel.js
├── models/enrollmentModel.js
├── controllers/checkoutController.js
├── controllers/reportController.js
├── routes/index.js           # router.post('/api/checkout', checkout)
└── middlewares/errorHandler.js
```
Cada model exporta funções puras de acesso a dados; controllers orquestram; rotas só mapeiam.

## T4 — Regra de negócio fora do controller/rota (Fat Controller → Service/Controller fino)

**Antes** (rota Flask com 60 linhas de validação + persistência + notificação via `print`):
```python
@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if len(data.get('title','')) < 3: return jsonify({'error':'...'}), 400
    # ... 40 linhas ...
    db.session.add(task); db.session.commit()
```

**Depois**:
```python
# routes/task_routes.py — só mapeamento
@task_bp.route('/tasks', methods=['POST'])
def create_task():
    task = task_service.create_task(request.get_json())
    return jsonify(task.to_dict()), 201

# services/task_service.py — validação + regra + persistência
def create_task(data):
    payload = validate_task_payload(data)      # levanta ValidationError -> handler central devolve 400
    task = Task(**payload)
    db.session.add(task)
    db.session.commit()
    return task
```

## T5 — Estado global mutável → conexão gerenciada por request

**Antes** (`database.py`):
```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(db_path, check_same_thread=False)
```

**Depois** (Flask `g` + teardown; schema/seed separados da obtenção de conexão):
```python
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db(app):          # chamado uma vez no composition root
    ...  # CREATE TABLEs + seed idempotente
```

## T6 — Error handling centralizado (matar try/except repetido e vazamento de `str(e)`)

**Antes**: todo handler com `except Exception as e: return jsonify({"erro": str(e)}), 500`.

**Depois**:
```python
# middlewares/error_handler.py
class ApiError(Exception):
    def __init__(self, message, status=400):
        self.message, self.status = message, status

def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api(e):
        return jsonify({"erro": e.message, "sucesso": False}), e.status

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        app.logger.exception(e)                      # detalhe vai pro log
        return jsonify({"erro": "Erro interno"}), 500  # cliente não vê internals
```
Express: middleware `(err, req, res, next)` registrado por último; controllers async com wrapper `next(err)`.

## T7 — Senhas: texto plano / MD5 / cripto caseira → hash forte

**Antes**:
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()          # MD5 sem salt
cursor.execute("... WHERE email = '"+e+"' AND senha = '"+s+"'") # texto plano
```

**Depois** (Python, sem dependência nova):
```python
from werkzeug.security import generate_password_hash, check_password_hash
self.password = generate_password_hash(pwd)
ok = check_password_hash(user.password, pwd)
```
Node sem dependência nova: `crypto.scryptSync(pwd, salt, 64)` com salt aleatório armazenado junto. Remover senha de qualquer `to_dict`/resposta de API e de logs.

## T8 — Queries N+1 → JOIN / eager loading

**Antes** (uma query por pedido, por item, por produto):
```python
for row in pedidos:
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (row["id"],))
    for item in itens:
        cursor3.execute("SELECT nome FROM produtos WHERE id = ?", (item["produto_id"],))
```

**Depois** (uma query com JOIN, agrupada em memória):
```python
cursor.execute("""
    SELECT p.*, i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
""")
```
SQLAlchemy: `Task.query.options(joinedload(Task.user), joinedload(Task.category))`. Agregações: `GROUP BY` em vez de loop de `count()`.

## T9 — Callback hell → async/await (promisificar o driver)

**Antes**: 5 níveis de callbacks aninhados + contadores manuais (`coursesPending--`) para decidir quando responder.

**Depois**:
```javascript
// db/connection.js
const { promisify } = require('node:util');
db.getAsync = promisify(db.get.bind(db));
db.allAsync = promisify(db.all.bind(db));

// controllers/checkoutController.js
async function checkout(req, res, next) {
  try {
    const course = await courseModel.findActive(db, courseId);
    if (!course) return res.status(404).send('Curso não encontrado');
    const user = await userModel.findOrCreate(db, name, email, password);
    const result = await checkoutService.process(db, user, course, card);
    res.status(200).json(result);
  } catch (err) { next(err); }
}
```
Substitui também a recomendação de API deprecated (sqlite3 callback API → wrapper promisificado).

## T10 — APIs deprecated → equivalente moderno

```python
# Antes                                   # Depois
datetime.utcnow()                          datetime.now(timezone.utc)   # (se o schema for naive: helper que remove tzinfo)
User.query.get(user_id)                    db.session.get(User, user_id)
@app.before_first_request                  inicialização no create_app()
```
```javascript
new Buffer(x)              →  Buffer.from(x)
bodyParser.json()          →  express.json()
```

## T11 — Duplicação → extração de função/validator único

**Antes**: o mesmo bloco "task está atrasada?" copiado em 4 rotas; a mesma serialização dict repetida.

**Depois**: um único `Task.is_overdue()` no model + `to_dict()` como única fonte de serialização; validação de payload num validator compartilhado (T4). Deletar as cópias.

## T12 — Magic numbers/strings → constantes nomeadas

**Antes**:
```python
if faturamento > 10000: desconto = faturamento * 0.1
elif faturamento > 5000: desconto = faturamento * 0.05
```

**Depois**:
```python
DISCOUNT_TIERS = [(10_000, 0.10), (5_000, 0.05), (1_000, 0.02)]  # (limiar, taxa)

def desconto_para(faturamento):
    for limiar, taxa in DISCOUNT_TIERS:
        if faturamento > limiar:
            return faturamento * taxa
    return 0
```
Listas de status/categorias válidas viram constantes num módulo só (importadas onde preciso). Imports mortos e helpers nunca usados: deletar. `print` de log → `app.logger` / logger da stack.
