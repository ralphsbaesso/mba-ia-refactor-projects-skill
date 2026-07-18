"""Testes de service: regra de negócio de pedido e relatório (caminho feliz + erro)."""

import pytest

from database import get_db
from middlewares.error_handler import ApiError
from models import produto as produto_model
from services import pedido_service
from services.relatorio_service import desconto_para


def test_criar_pedido_calcula_total_e_baixa_estoque(app):
    with app.app_context():
        db = get_db()
        estoque_antes = produto_model.get_by_id(db, 2)["estoque"]
        resultado = pedido_service.criar_pedido(db, 2, [{"produto_id": 2, "quantidade": 3}])
        assert resultado["total"] == pytest.approx(89.90 * 3)
        assert produto_model.get_by_id(db, 2)["estoque"] == estoque_antes - 3


def test_criar_pedido_estoque_insuficiente(app):
    with app.app_context():
        with pytest.raises(ApiError) as exc:
            pedido_service.criar_pedido(get_db(), 2, [{"produto_id": 6, "quantidade": 9999}])
        assert exc.value.status == 400
        assert "Estoque insuficiente" in exc.value.message


def test_criar_pedido_produto_inexistente(app):
    with app.app_context():
        with pytest.raises(ApiError) as exc:
            pedido_service.criar_pedido(get_db(), 2, [{"produto_id": 99999, "quantidade": 1}])
        assert exc.value.status == 400


def test_desconto_por_faixa():
    assert desconto_para(12000) == pytest.approx(1200)  # 10%
    assert desconto_para(6000) == pytest.approx(300)     # 5%
    assert desconto_para(1500) == pytest.approx(30)      # 2%
    assert desconto_para(500) == 0                       # sem desconto
