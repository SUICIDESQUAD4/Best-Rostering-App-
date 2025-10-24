# App/views/system_views.py
from flask import Blueprint, jsonify
from App.controllers import initialize

system_bp = Blueprint('system_bp', __name__, url_prefix="/system")


@system_bp.route('/init', methods=['POST'])
def initialize_app():
    initialize()
    response = jsonify({
        "message": "System initialized successfully",
    })
    return response, 200

