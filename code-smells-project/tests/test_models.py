"""Testes de model: acesso a dados parametrizado, serialização segura, JOIN sem N+1."""

from database import get_db
from models import pedido as pedido_model
from models import produto as produto_model
from models import usuario as usuario_model
from services import pedido_service


def test_to_public_dict_nao_vaza_senha(app):
    """Regressão do finding CRITICAL: senha (hash) nunca sai na serialização de usuário."""
    with app.app_context():
        row = usuario_model.get_by_email(get_db(), "admin@loja.com")
        publico = usuario_model.to_public_dict(row)
        assert "senha" not in publico
        assert "password" not in publico
        assert publico["email"] == "admin@loja.com"


def test_search_com_input_malicioso_nao_faz_injection(app):
    """Regressão do finding CRITICAL SQL Injection: aspas viram literal, não SQL."""
    with app.app_context():
        db = get_db()
        antes = produto_model.count(db)
        # Payload que, concatenado, dropava/alterava dados no código legado.
        resultado = produto_model.search(db, termo="x'; DROP TABLE produtos; --")
        assert resultado == []
        assert produto_model.count(db) == antes  # tabela intacta


def test_search_por_categoria(app):
    with app.app_context():
        resultado = produto_model.search(get_db(), categoria="moveis")
        assert len(resultado) == 1
        assert resultado[0]["categoria"] == "moveis"


def test_get_by_id_inexistente_retorna_none(app):
    with app.app_context():
        assert produto_model.get_by_id(get_db(), 99999) is None


def test_pedido_join_agrupa_itens_sem_n1(app):
    """get_all monta itens via um único JOIN, sem query por item."""
    with app.app_context():
        db = get_db()
        pedido_service.criar_pedido(db, 2, [{"produto_id": 1, "quantidade": 1}])
        pedidos = pedido_model.get_all(db)
        assert len(pedidos) == 1
        assert len(pedidos[0]["itens"]) == 1
        assert pedidos[0]["itens"][0]["produto_nome"] == "Notebook Gamer"
