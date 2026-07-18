from flask import Blueprint

from controllers import health_controller as ctrl

main_bp = Blueprint("main", __name__)

main_bp.add_url_rule("/", "index", ctrl.index, methods=["GET"])
main_bp.add_url_rule("/health", "health_check", ctrl.health_check, methods=["GET"])
