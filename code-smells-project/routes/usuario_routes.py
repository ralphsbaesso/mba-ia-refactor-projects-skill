from flask import Blueprint

from controllers import usuario_controller as ctrl

usuario_bp = Blueprint("usuarios", __name__)

usuario_bp.add_url_rule("/usuarios", "listar", ctrl.listar, methods=["GET"])
usuario_bp.add_url_rule("/usuarios/<int:id>", "buscar", ctrl.buscar, methods=["GET"])
usuario_bp.add_url_rule("/usuarios", "criar", ctrl.criar, methods=["POST"])
usuario_bp.add_url_rule("/login", "login", ctrl.login, methods=["POST"])
