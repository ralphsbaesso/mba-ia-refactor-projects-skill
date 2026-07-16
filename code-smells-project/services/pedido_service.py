"""Regra de negócio de pedidos (checagem de estoque, cálculo de total, baixa)."""

from middlewares.error_handler import ApiError
from models import pedido as pedido_model
from models import produto as produto_model


def criar_pedido(db, usuario_id, itens):
    total = 0
    produtos = {}

    for item in itens:
        produto = produto_model.get_by_id(db, item["produto_id"])
        if produto is None:
            raise ApiError(f"Produto {item['produto_id']} não encontrado", 400)
        if produto["estoque"] < item["quantidade"]:
            raise ApiError(f"Estoque insuficiente para {produto['nome']}", 400)
        produtos[item["produto_id"]] = produto
        total += produto["preco"] * item["quantidade"]

    pedido_id = pedido_model.insert_pedido(db, usuario_id, total)
    for item in itens:
        produto = produtos[item["produto_id"]]
        pedido_model.insert_item(
            db, pedido_id, item["produto_id"], item["quantidade"], produto["preco"]
        )
        produto_model.decrement_estoque(db, item["produto_id"], item["quantidade"])
    db.commit()

    return {"pedido_id": pedido_id, "total": total}
