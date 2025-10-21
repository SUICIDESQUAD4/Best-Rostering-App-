# App/views/auth_views.py
from flask import Blueprint, request, jsonify, make_response
from App.controllers.auth_controller import authenticate

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/v1')

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login route for both Admin and Staff."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    token, user = authenticate(username, password, role)
    if not token:
        return jsonify({"error": "Invalid credentials"}), 401

    resp = make_response(jsonify({
        "access_token": token,
        "userId": user.userId,
        "username": user.username,
        "type": user.type
    }))
    resp.set_cookie("access_token_cookie", token, httponly=False)
    return resp
