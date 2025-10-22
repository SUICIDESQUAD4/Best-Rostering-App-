# App/views/auth_views.py
from flask import Blueprint, request, jsonify, make_response
from App.controllers.auth_controller import authenticate_user

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    token, user = authenticate_user(username, password, "admin")
    if not token:
        return jsonify({"error": "Invalid admin credentials"}), 401

    resp = make_response(jsonify({
        "access_token": token,
        "userId": user.userId,
        "username": user.username,
        "type": user.type
    }))
    resp.set_cookie("access_token_cookie", token, httponly=False)
    return resp

@auth_bp.route('/admin/logout', methods=['POST'])
def admin_logout():
    resp = make_response(jsonify({"message": "Admin logged out"}))
    resp.delete_cookie("access_token_cookie")
    return resp, 200


@auth_bp.route('/staff/login', methods=['POST'])
def staff_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    token, user = authenticate_user(username, password, "staff")
    if not token:
        return jsonify({"error": "Invalid staff credentials"}), 401

    resp = make_response(jsonify({
        "access_token": token,
        "userId": user.userId,
        "username": user.username,
        "type": user.type
    }))
    resp.set_cookie("access_token_cookie", token, httponly=False)
    return resp

@auth_bp.route('/staff/logout', methods=['POST'])
def staff_logout():
    resp = make_response(jsonify({"message": "Staff logged out"}))
    resp.delete_cookie("access_token_cookie")
    return resp, 200
