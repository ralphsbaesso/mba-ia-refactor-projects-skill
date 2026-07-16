from flask import current_app, jsonify, request

from database import get_db
from middlewares.error_handler import ApiError
from models import pedido as pedido_model
from services import pedido_service
from utils.validators import validar_status_pedido


def criar():
    dados = request.get_json(silent=True)
    if not dados:
        raise ApiError("Dados inválidos", 400)

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        raise ApiError("Usuario ID é obrigatório", 400)
    if not itens:
        raise ApiError("Pedido deve ter pelo menos 1 item", 400)

    resultado = pedido_service.criar_pedido(get_db(), usuario_id, itens)
    current_app.logger.info(
        "Pedido %s criado para usuario %s", resultado["pedido_id"], usuario_id
    )
    return jsonify(
        {"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}
    ), 201


def listar_por_usuario(usuario_id):
    pedidos = pedido_model.get_by_usuario(get_db(), usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def listar_todos():
    pedidos = pedido_model.get_all(get_db())
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def atualizar_status(pedido_id):
    dados = request.get_json(silent=True) or {}
    novo_status = validar_status_pedido(dados.get("status", ""))
    pedido_model.update_status(get_db(), pedido_id, novo_status)
    current_app.logger.info("Pedido %s atualizado para status %s", pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
