from flask import jsonify

from database import get_db
from services import relatorio_service


def vendas():
    relatorio = relatorio_service.gerar_relatorio(get_db())
    return jsonify({"dados": relatorio, "sucesso": True}), 200
