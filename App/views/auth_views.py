# App/views/auth_views.py
from flask import Blueprint, request, jsonify
from App.controllers.auth_controller import authenticate

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    auth_result = authenticate(username, password)
    if auth_result is None:
        return jsonify({"msg": "Invalid credentials"}), 401

    return jsonify(auth_result), 200
