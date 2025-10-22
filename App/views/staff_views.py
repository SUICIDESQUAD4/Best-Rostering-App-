# App/views/staff_views.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from App.controllers import staff_controller

staff_bp = Blueprint('staff_bp', __name__, url_prefix="/staff")

def is_staff():
    return current_user and getattr(current_user, "type", None) == "staff"

@staff_bp.route('/login', methods=['POST'])
def staff_login():
    data = request.get_json()
    token, user = authenticate_user(data['username'], data['password'], "staff")
    if not token:
        return jsonify({"error": "Invalid credentials"}), 401
    resp = make_response(jsonify({"access_token": token, "userId": user.userId}))
    resp.set_cookie("access_token_cookie", token, httponly=False)
    return resp


@staff_bp.route('/profile', methods=['GET'])
@jwt_required()
def view_profile():
    if not is_staff():
        return jsonify({"error": "Staff only"}), 403
    return jsonify(staff_controller.get_profile(current_user.userId)), 200

@staff_bp.route('/roster', methods=['GET'])
@jwt_required()
def view_roster():
    if not is_staff():
        return jsonify({"error": "Staff only"}), 403
    week_start = request.args.get("week_start")
    return jsonify(staff_controller.view_roster(week_start)), 200

@staff_bp.route('/my-shifts', methods=['GET'])
@jwt_required()
def my_shifts():
    if not is_staff():
        return jsonify({"error": "Staff only"}), 403
    return jsonify(staff_controller.view_my_shifts(current_user.userId)), 200

@staff_bp.route('/shifts/<int:shift_id>/time-in', methods=['POST'])
@jwt_required()
def time_in(shift_id):
    if not is_staff():
        return jsonify({"error": "Staff only"}), 403
    ts = request.json.get("timestamp") if request.json else None
    return jsonify(staff_controller.time_in(current_user.userId, shift_id, ts)), 200

@staff_bp.route('/shifts/<int:shift_id>/time-out', methods=['POST'])
@jwt_required()
def time_out(shift_id):
    if not is_staff():
        return jsonify({"error": "Staff only"}), 403
    ts = request.json.get("timestamp") if request.json else None
    return jsonify(staff_controller.time_out(current_user.userId, shift_id, ts)), 200
