from flask import current_app, jsonify, request

from database import get_db
from middlewares.error_handler import ApiError
from models import produto as produto_model
from utils.validators import validar_produto


def listar():
    produtos = produto_model.get_all(get_db())
    current_app.logger.info("Listando %d produtos", len(produtos))
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar(id):
    produto = produto_model.get_by_id(get_db(), id)
    if not produto:
        raise ApiError("Produto não encontrado", 404)
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar():
    dados = validar_produto(request.get_json(silent=True), completo=True)
    novo_id = produto_model.create(
        get_db(),
        dados["nome"],
        dados["descricao"],
        dados["preco"],
        dados["estoque"],
        dados["categoria"],
    )
    current_app.logger.info("Produto criado com ID: %s", novo_id)
    return jsonify({"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar(id):
    db = get_db()
    if not produto_model.get_by_id(db, id):
        raise ApiError("Produto não encontrado", 404)
    dados = validar_produto(request.get_json(silent=True), completo=False)
    produto_model.update(
        db,
        id,
        dados["nome"],
        dados["descricao"],
        dados["preco"],
        dados["estoque"],
        dados["categoria"],
    )
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar(id):
    db = get_db()
    if not produto_model.get_by_id(db, id):
        raise ApiError("Produto não encontrado", 404)
    produto_model.delete(db, id)
    current_app.logger.info("Produto %s deletado", id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)

    preco_min = float(preco_min) if preco_min else None
    preco_max = float(preco_max) if preco_max else None

    resultados = produto_model.search(get_db(), termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
