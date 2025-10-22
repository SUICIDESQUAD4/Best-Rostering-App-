# App/views/admin_views.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from App.models import Staff, Shift, Roster
from App.database import db
from datetime import datetime

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/api/admin')

@admin_bp.route('/staff', methods=['POST'])
@jwt_required()
def create_staff():
    data = request.get_json()
    if Staff.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 400

    staff = Staff(username=data['username'], email=data['email'], role=data['role'], type='staff')
    staff.set_password(data['password'])
    db.session.add(staff)
    db.session.commit()
    return jsonify({"message": "Staff created successfully", "userId": staff.userId}), 201

@admin_bp.route('/staff', methods=['GET'])
@jwt_required()
def list_staff():
    staff_list = Staff.query.all()
    return jsonify([s.get_json() for s in staff_list]), 200

@admin_bp.route('/staff/<int:staff_id>', methods=['DELETE'])
@jwt_required()
def delete_staff(staff_id):
    staff = Staff.query.get(staff_id)
    if not staff:
        return jsonify({"error": "Staff not found"}), 404
    db.session.delete(staff)
    db.session.commit()
    return jsonify({"message": "Staff deleted successfully"}), 200

@admin_bp.route('/schedule', methods=['POST'])
@jwt_required()
def schedule_shift():
    data = request.get_json()
    staff = Staff.query.get(data['staffId'])
    if not staff:
        return jsonify({"error": "Invalid staff ID"}), 400
    start = datetime.fromisoformat(data['startTime'])
    end = datetime.fromisoformat(data['endTime'])
    roster = Roster.query.order_by(Roster.weekStartDate.desc()).first()
    shift = Shift(staffId=staff.userId, rosterId=roster.rosterId, startTime=start, endTime=end)
    db.session.add(shift)
    db.session.commit()
    return jsonify({"message": "Shift scheduled successfully", "shiftId": shift.shiftId}), 201

@admin_bp.route('/shifts', methods=['GET'])
@jwt_required()
def list_shifts():
    shifts = Shift.query.all()
    return jsonify([{
        "shiftId": s.shiftId,
        "staffName": s.staff.username if s.staff else "Unassigned",
        "start": s.startTime,
        "end": s.endTime
    } for s in shifts]), 200

@admin_bp.route('/report/week', methods=['GET'])
@jwt_required()
def weekly_report():
    roster = Roster.query.order_by(Roster.weekStartDate.desc()).first()
    if not roster:
        return jsonify({"error": "No roster found"}), 404
    total_shifts = len(roster.shifts)
    return jsonify({
        "weekStart": str(roster.weekStartDate),
        "totalShifts": total_shifts,
        "absentCount": 2,
        "lateCount": 1
    }), 200
