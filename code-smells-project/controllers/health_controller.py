from flask import current_app, jsonify

from database import get_db
from models import pedido as pedido_model
from models import produto as produto_model
from models import usuario as usuario_model


def index():
    return jsonify(
        {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }
    )


def health_check():
    db = get_db()
    return jsonify(
        {
            "status": "ok",
            "database": "connected",
            "counts": {
                "produtos": produto_model.count(db),
                "usuarios": usuario_model.count(db),
                "pedidos": pedido_model.count(db),
            },
            "versao": "1.0.0",
            "ambiente": current_app.config["ENV"],
        }
    ), 200
