from flask import Blueprint

from controllers import produto_controller as ctrl

produto_bp = Blueprint("produtos", __name__)

produto_bp.add_url_rule("/produtos", "listar", ctrl.listar, methods=["GET"])
produto_bp.add_url_rule("/produtos/busca", "buscar_produtos", ctrl.buscar_produtos, methods=["GET"])
produto_bp.add_url_rule("/produtos/<int:id>", "buscar", ctrl.buscar, methods=["GET"])
produto_bp.add_url_rule("/produtos", "criar", ctrl.criar, methods=["POST"])
produto_bp.add_url_rule("/produtos/<int:id>", "atualizar", ctrl.atualizar, methods=["PUT"])
produto_bp.add_url_rule("/produtos/<int:id>", "deletar", ctrl.deletar, methods=["DELETE"])
