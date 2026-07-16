from flask import current_app, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db
from middlewares.error_handler import ApiError
from models import usuario as usuario_model
from utils.validators import validar_usuario


def listar():
    usuarios = usuario_model.get_all(get_db())
    return jsonify({"dados": usuarios, "sucesso": True}), 200


def buscar(id):
    usuario = usuario_model.get_by_id(get_db(), id)
    if not usuario:
        raise ApiError("Usuário não encontrado", 404)
    return jsonify({"dados": usuario, "sucesso": True}), 200


def criar():
    dados = validar_usuario(request.get_json(silent=True))
    novo_id = usuario_model.create(
        get_db(),
        dados["nome"],
        dados["email"],
        generate_password_hash(dados["senha"]),
    )
    current_app.logger.info("Usuário criado: %s", dados["email"])
    return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201


def login():
    dados = request.get_json(silent=True) or {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        raise ApiError("Email e senha são obrigatórios", 400)

    row = usuario_model.get_by_email(get_db(), email)
    if row is None or not check_password_hash(row["senha"], senha):
        current_app.logger.info("Login falhou: %s", email)
        raise ApiError("Email ou senha inválidos", 401)

    current_app.logger.info("Login bem-sucedido: %s", email)
    return jsonify(
        {"dados": usuario_model.to_public_dict(row), "sucesso": True, "mensagem": "Login OK"}
    ), 200
