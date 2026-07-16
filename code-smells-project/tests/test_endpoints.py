"""Testes de contrato via test client — regressão dos endpoints originais."""


def test_listar_produtos(client):
    resp = client.get("/produtos")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["sucesso"] is True
    assert len(body["dados"]) == 10


def test_buscar_produto_inexistente_404(client):
    resp = client.get("/produtos/99999")
    assert resp.status_code == 404


def test_criar_produto_valida_categoria(client):
    resp = client.post("/produtos", json={"nome": "Item", "preco": 10, "estoque": 1, "categoria": "invalida"})
    assert resp.status_code == 400


def test_login_com_senha_correta(client):
    resp = client.post("/login", json={"email": "admin@loja.com", "senha": "admin123"})
    assert resp.status_code == 200
    assert resp.get_json()["dados"]["email"] == "admin@loja.com"


def test_login_com_senha_errada_401(client):
    resp = client.post("/login", json={"email": "admin@loja.com", "senha": "errada"})
    assert resp.status_code == 401


def test_listar_usuarios_nao_expoe_senha(client):
    """Regressão: nenhum usuário serializado pode conter o campo senha."""
    resp = client.get("/usuarios")
    assert resp.status_code == 200
    for usuario in resp.get_json()["dados"]:
        assert "senha" not in usuario


def test_health_nao_vaza_secret(client):
    """Regressão do finding CRITICAL: /health não devolve mais o secret nem debug."""
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "secret_key" not in body
    assert "debug" not in body
    assert body["status"] == "ok"


def test_endpoint_admin_query_removido(client):
    """O endpoint de SQL arbitrário foi removido (não deve mais existir)."""
    resp = client.post("/admin/query", json={"sql": "SELECT 1"})
    assert resp.status_code == 404


def test_relatorio_vendas(client):
    resp = client.get("/relatorios/vendas")
    assert resp.status_code == 200
    assert "faturamento_bruto" in resp.get_json()["dados"]


def test_criar_e_listar_pedido(client):
    criar = client.post("/pedidos", json={"usuario_id": 2, "itens": [{"produto_id": 1, "quantidade": 1}]})
    assert criar.status_code == 201
    listar = client.get("/pedidos")
    assert listar.status_code == 200
    assert len(listar.get_json()["dados"]) == 1
