"""Validação de payloads centralizada (DRY) — levanta ApiError para o handler central."""

from middlewares.error_handler import ApiError
from utils.constants import (
    CATEGORIAS_VALIDAS,
    NOME_PRODUTO_MAX,
    NOME_PRODUTO_MIN,
    STATUS_PEDIDO_VALIDOS,
)


def validar_produto(dados, completo=True):
    """Valida e normaliza o payload de produto.

    `completo=True` aplica também as regras de tamanho de nome e categoria válida
    (usado na criação); `completo=False` mantém o comportamento mais brando da
    atualização original.
    """
    if not dados:
        raise ApiError("Dados inválidos", 400)
    if "nome" not in dados:
        raise ApiError("Nome é obrigatório", 400)
    if "preco" not in dados:
        raise ApiError("Preço é obrigatório", 400)
    if "estoque" not in dados:
        raise ApiError("Estoque é obrigatório", 400)

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        raise ApiError("Preço não pode ser negativo", 400)
    if estoque < 0:
        raise ApiError("Estoque não pode ser negativo", 400)

    if completo:
        if len(nome) < NOME_PRODUTO_MIN:
            raise ApiError("Nome muito curto", 400)
        if len(nome) > NOME_PRODUTO_MAX:
            raise ApiError("Nome muito longo", 400)
        if categoria not in CATEGORIAS_VALIDAS:
            raise ApiError(f"Categoria inválida. Válidas: {CATEGORIAS_VALIDAS}", 400)

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def validar_usuario(dados):
    if not dados:
        raise ApiError("Dados inválidos", 400)
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not nome or not email or not senha:
        raise ApiError("Nome, email e senha são obrigatórios", 400)
    return {"nome": nome, "email": email, "senha": senha}


def validar_status_pedido(status):
    if status not in STATUS_PEDIDO_VALIDOS:
        raise ApiError("Status inválido", 400)
    return status
