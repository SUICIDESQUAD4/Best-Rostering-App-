# App/views/auth_views.py
from flask import Blueprint, request, jsonify, make_response
from App.controllers.auth_controller import authenticate

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login route for both Admin and Staff.
    Returns a JWT access token and basic user info.
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')  # optional

    # Authenticate user
    result = authenticate(username, password, role)

    # Normalize output (handle either tuple or None)
    if not result:
        return jsonify({"error": "Invalid credentials"}), 401
    if isinstance(result, tuple):
        token, user = result
    else:
        token, user = result, None

    # Build response
    response_data = {
        "access_token": token,
        "userId": user.userId if user else None,
        "username": user.username if user else username,
        "type": user.type if user else role
    }

    resp = make_response(jsonify(response_data))
    # Optional: Set JWT token in cookie for web UI
    resp.set_cookie("access_token_cookie", token, httponly=False)

    return resp
