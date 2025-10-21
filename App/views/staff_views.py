# App/views/staff_views.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.models import Staff, Shift, AttendanceRecord
from App.database import db
from datetime import datetime

staff_bp = Blueprint('staff_bp', __name__, url_prefix='/api/staff')

@staff_bp.route('/me', methods=['GET'])
@jwt_required()
def my_profile():
    user_id = get_jwt_identity()
    staff = Staff.query.get(user_id)
    return jsonify(staff.get_json()), 200

@staff_bp.route('/shifts', methods=['GET'])
@jwt_required()
def my_shifts():
    user_id = get_jwt_identity()
    shifts = Shift.query.filter_by(staffId=user_id).all()
    return jsonify([{
        "shiftId": s.shiftId,
        "startTime": s.startTime,
        "endTime": s.endTime
    } for s in shifts]), 200

@staff_bp.route('/attendance/time-in', methods=['POST'])
@jwt_required()
def time_in():
    user_id = get_jwt_identity()
    data = request.get_json()
    record = AttendanceRecord.get_or_create(user_id, data['shiftId'])
    record.markTimeIn(datetime.utcnow())
    db.session.commit()
    return jsonify({"message": "Time-in recorded successfully"}), 200

@staff_bp.route('/attendance/time-out', methods=['POST'])
@jwt_required()
def time_out():
    user_id = get_jwt_identity()
    data = request.get_json()
    record = AttendanceRecord.get_or_create(user_id, data['shiftId'])
    record.markTimeOut(datetime.utcnow())
    db.session.commit()
    return jsonify({"message": "Time-out recorded successfully"}), 200
