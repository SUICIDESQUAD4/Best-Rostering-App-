# App/views/admin_views.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user
from App.controllers import admin_controller


admin_bp = Blueprint('admin_bp', __name__, url_prefix="/admin")

def is_admin():
    return current_user and getattr(current_user, "type", None) == "admin"

@admin_bp.route('/staff', methods=['GET'])
@jwt_required()
def list_staff():
    if not is_admin():
        return jsonify({"error": "Admins only"}), 403
    return jsonify(admin_controller.list_staff()), 200

@admin_bp.route('/staff', methods=['POST'])
@jwt_required()
def add_staff():
    if not is_admin():
        return jsonify({"error": "Admins only"}), 403
    data = request.get_json()
    return jsonify(admin_controller.create_staff(data)), 201

@admin_bp.route('/staff/<int:staff_id>', methods=['DELETE'])
@jwt_required()
def delete_staff(staff_id):
    if not is_admin():
        return jsonify({"error": "Admins only"}), 403
    ok = admin_controller.delete_staff(staff_id)
    if not ok:
        return jsonify({"error": "Staff not found"}), 404
    return jsonify({"message": "Staff deleted"}), 200

@admin_bp.route('/shifts', methods=['POST'])
@jwt_required()
def schedule_shift():
    if not is_admin():
        return jsonify({"error": "Admins only"}), 403
    data = request.get_json()
    shift = admin_controller.schedule_shift(data)
    return jsonify(shift), 201

@admin_bp.route('/shifts', methods=['GET'])
@jwt_required()
def list_shifts():
    if not is_admin():
        return jsonify({"error": "Admins only"}), 403
    return jsonify(admin_controller.list_shifts()), 200

@admin_bp.route('/roster/<int:roster_id>/report', methods=['POST'])
@jwt_required()
def generate_report(roster_id):
    if not is_admin():
        return jsonify({"error": "Admins only"}), 403
    report = admin_controller.generate_shift_report(roster_id)
    return report, 201
