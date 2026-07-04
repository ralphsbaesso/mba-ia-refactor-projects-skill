# Guidelines de Testes Unitários

Regras para a geração de testes ao final da Fase 3. O objetivo é **garantir que o comportamento foi preservado** após a refatoração: os testes exercitam as regras de negócio extraídas para as novas camadas (models e services/controllers) e complementam — nunca substituem — a validação de boot + endpoints.

## Princípios

1. **Teste comportamento, não implementação**: cubra as regras de negócio que a refatoração moveu para models/services (cálculo de desconto, validação de payload, "task atrasada?", processo de checkout, hashing de senha), não getters triviais.
2. **Priorize o que tinha bug/severidade alta**: cada finding CRITICAL/HIGH corrigido é candidato natural a um teste de regressão (ex.: senha nunca sai em `to_dict`, query parametrizada, secret vindo de env).
3. **Isolamento**: testes de model/service não devem depender de servidor rodando. Use banco em memória / fixtures. Testes de endpoint usam o test client do framework.
4. **Determinismo**: sem rede, sem relógio real acoplado (injete/mock `datetime` quando a regra depender de tempo), sem ordem entre testes.
5. **Rápido de rodar e óbvio de invocar**: um único comando (`pytest`, `npm test`) documentado no manifesto.

## Ferramenta por stack (detectada na Fase 1)

| Stack | Runner | Extras | Comando |
|---|---|---|---|
| Python / Flask | `pytest` | `pytest-flask` quando testar endpoints via app factory | `pytest` |
| Node.js / Express | `jest` (ou `vitest`) | `supertest` para endpoints HTTP | `npm test` |
| Outra stack | runner mais consolidado da linguagem (Go: `testing`; Ruby: `rspec`; ...) | — | comando idiomático |

Escolha sempre a ferramenta mais consolidada da stack. Não introduza um runner exótico.

## O que cobrir (mínimo)

- **Camada de model**: pelo menos 1 regra de negócio por entidade relevante + 1 teste de serialização segura (`to_dict` não vaza senha/campos sensíveis).
- **Camada de service/controller**: caminho feliz + pelo menos 1 caminho de erro (validação falha → erro de domínio; recurso inexistente → 404).
- **Regressão dos findings CRITICAL/HIGH**: um teste que falharia no código legado e passa no refatorado (ex.: injeção de SQL, senha em texto plano, secret hardcoded).

Não persiga cobertura de 100%; persiga cobrir as regras que, se quebrarem, quebram o contrato da aplicação.

## Manifesto e execução (OBRIGATÓRIO)

- **Adicione a dependência de teste ao manifesto**:
  - Python: acrescente `pytest` (e `pytest-flask` se usado) a `requirements.txt`.
  - Node: acrescente `jest`/`vitest` e `supertest` a `devDependencies` do `package.json` e defina `"scripts": { "test": "jest" }` (ou `vitest run`).
- **Documente o comando de execução** no output da Fase 3 e no README do projeto quando aplicável.
- Coloque os testes numa pasta convencional: Python → `tests/`; Node → `tests/` ou `__tests__/`.

---

## Python / Flask — pytest

### Estrutura sugerida
```
tests/
├── conftest.py            # fixtures: app, client, banco em memória/seed
├── test_models.py
└── test_services.py       # ou test_controllers.py
```

### Fixtures (app factory + banco isolado)
```python
# tests/conftest.py
import pytest
from app import create_app          # composition root exposto pela refatoração
from database import init_db, get_db

@pytest.fixture
def app():
    app = create_app({"TESTING": True, "DATABASE_PATH": ":memory:"})
    with app.app_context():
        init_db(app)                 # cria schema + seed idempotente
    yield app

@pytest.fixture
def client(app):
    return app.test_client()
```
Em projetos com Flask-SQLAlchemy, a fixture usa `db.create_all()`/`db.drop_all()` dentro do `app_context` e uma URI `sqlite:///:memory:`.

### Teste de model (regra de negócio + serialização segura)
```python
# tests/test_models.py
from models.task_model import Task

def test_is_overdue_true_when_past_due(app):
    from datetime import datetime, timedelta, timezone
    t = Task(title="x", due_date=datetime.now(timezone.utc) - timedelta(days=1), done=False)
    assert t.is_overdue() is True

def test_to_dict_never_leaks_password(app):
    from models.user_model import User
    u = User(email="a@b.com"); u.set_password("segredo")
    assert "password" not in u.to_dict()
    assert "senha" not in u.to_dict()
```

### Teste de service (caminho feliz + erro de domínio)
```python
# tests/test_services.py
import pytest
from services.task_service import create_task
from middlewares.error_handler import ApiError

def test_create_task_ok(app):
    with app.app_context():
        task = create_task({"title": "Comprar pão", "priority": "high"})
        assert task.id is not None

def test_create_task_rejects_short_title(app):
    with app.app_context():
        with pytest.raises(ApiError) as exc:
            create_task({"title": "ab"})
        assert exc.value.status == 400
```

### Teste de endpoint (opcional, via test client — regressão de contrato)
```python
def test_list_tasks_returns_200(client):
    resp = client.get("/tasks")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)
```

---

## Node.js / Express — jest + supertest

### Estrutura sugerida
```
tests/
├── models.test.js
├── checkout.test.js       # service/controller
└── endpoints.test.js      # supertest contra o app exportado (sem listen)
```
Pré-requisito da refatoração (T3): `app.js` **exporta** o `app` montado sem chamar `listen` — o `listen` fica no entry point. Isso permite `supertest(app)`.

### package.json
```json
{
  "scripts": { "start": "node src/server.js", "test": "jest" },
  "devDependencies": { "jest": "^29", "supertest": "^7" }
}
```

### Teste de model (função pura de acesso a dados / regra)
```javascript
// tests/models.test.js
const { openTestDb } = require('../src/db/connection');
const courseModel = require('../src/models/courseModel');

test('findActive retorna null para curso inativo', async () => {
  const db = await openTestDb();               // :memory:, schema+seed aplicados
  const course = await courseModel.findActive(db, /* id inativo */ 999);
  expect(course).toBeNull();
});
```

### Teste de service (regra de negócio de checkout)
```javascript
// tests/checkout.test.js
const checkoutService = require('../src/services/checkoutService');

test('aplica desconto por faixa de faturamento', () => {
  expect(checkoutService.discountFor(12000)).toBeCloseTo(1200); // 10%
  expect(checkoutService.discountFor(6000)).toBeCloseTo(300);   //  5%
  expect(checkoutService.discountFor(500)).toBe(0);
});
```

### Teste de endpoint (supertest — regressão de contrato)
```javascript
// tests/endpoints.test.js
const request = require('supertest');
const app = require('../src/app');            // app exportado sem listen

test('POST /api/checkout com curso inexistente devolve 404', async () => {
  const res = await request(app)
    .post('/api/checkout')
    .send({ courseId: 999, name: 'x', email: 'x@y.com' });
  expect(res.status).toBe(404);
});
```

---

## Regra de fechamento

Os testes fazem parte da validação da Fase 3. A fase **não está completa** enquanto `pytest` / `npm test` não rodarem com **todos os testes passando**, além do boot + endpoints respondendo. Se um teste falhar, corrija o código refatorado (não relaxe o teste para verde artificial).
