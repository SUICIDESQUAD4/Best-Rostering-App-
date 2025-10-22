# App/views/staff_views.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from datetime import datetime, date

from App.controllers.staff_controller import (
    list_staff, get_staff, create_staff, update_staff, delete_staff,
    get_current_roster, get_roster_by_weekstart,
    schedule_shift_for_staff, mark_time_in, mark_time_out, generate_shift_report_for_roster
)
from App.database import db
from App.models.roster import Roster
from App.models.shift import Shift
from App.models.staff import Staff

# ✅ Blueprint MUST use the prefix "api/v1"
staff_bp = Blueprint("staff_bp", __name__)

def is_admin(user):
    return getattr(user, "type", None) == "admin"


# ----------------- ADMIN ROUTES -----------------

@staff_bp.route("/staff", methods=["GET"])
@jwt_required()
def api_list_staff():
    if not is_admin(current_user):
        return jsonify({"msg": "admin only"}), 403
    return jsonify(list_staff()), 200


@staff_bp.route("/staff", methods=["POST"])
@jwt_required()
def api_create_staff():
    if not is_admin(current_user):
        return jsonify({"msg": "admin only"}), 403
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    role = data.get("role", "")
    if not (username and password and email):
        return jsonify({"msg": "username, password and email are required"}), 400
    try:
        staff = create_staff(username, password, email, role)
    except Exception as e:
        return jsonify({"msg": str(e)}), 400
    return jsonify(staff.to_dict()), 201


@staff_bp.route("/staff/<int:staff_id>", methods=["GET"])
@jwt_required()
def api_get_staff(staff_id):
    if not is_admin(current_user) and current_user.userId != staff_id:
        return jsonify({"msg": "forbidden"}), 403
    s = get_staff(staff_id)
    if not s:
        return jsonify({"msg": "not found"}), 404
    return jsonify(s.to_dict()), 200


@staff_bp.route("/staff/<int:staff_id>", methods=["PUT"])
@jwt_required()
def api_update_staff(staff_id):
    if not is_admin(current_user) and current_user.userId != staff_id:
        return jsonify({"msg": "forbidden"}), 403
    data = request.get_json() or {}
    s = update_staff(staff_id, **data)
    if not s:
        return jsonify({"msg": "not found"}), 404
    return jsonify(s.to_dict()), 200


@staff_bp.route("/staff/<int:staff_id>", methods=["DELETE"])
@jwt_required()
def api_delete_staff(staff_id):
    if not is_admin(current_user):
        return jsonify({"msg": "admin only"}), 403
    ok = delete_staff(staff_id)
    if not ok:
        return jsonify({"msg": "not found"}), 404
    return jsonify({"msg": "deleted"}), 200


# ----------------- ROSTER & ATTENDANCE -----------------

@staff_bp.route("/roster", methods=["GET"])
@jwt_required()
def api_get_roster():
    week_start = request.args.get("week_start")
    if week_start:
        try:
            ws = date.fromisoformat(week_start)
        except Exception:
            return jsonify({"msg": "invalid date format"}), 400
        roster = get_roster_by_weekstart(ws)
    else:
        roster = get_current_roster()
    if not roster:
        return jsonify({"msg": "no roster found"}), 404

    shifts = roster.getCombinedRoster()
    result = []
    for sh in shifts:
        staff_obj = db.session.get(Staff, sh.staffId)
        staff_name = staff_obj.username if staff_obj else None
        result.append({
            "shiftId": sh.shiftId,
            "staffId": sh.staffId,
            "staffName": staff_name,
            "startTime": sh.startTime.isoformat(),
            "endTime": sh.endTime.isoformat()
        })
    return jsonify({
        "weekStart": roster.weekStartDate.isoformat(),
        "weekEnd": roster.weekEndDate.isoformat(),
        "shifts": result
    }), 200


@staff_bp.route("/shifts/<int:shift_id>/time-in", methods=["POST"])
@jwt_required()
def api_time_in(shift_id):
    uid = current_user.userId
    sh = db.session.get(Shift, shift_id)
    if not sh:
        return jsonify({"msg": "shift not found"}), 404
    if current_user.type != "admin" and sh.staffId != uid:
        return jsonify({"msg": "forbidden"}), 403

    data = request.get_json() or {}
    ts = data.get("timestamp")
    ts_dt = datetime.fromisoformat(ts) if ts else datetime.utcnow()

    rec = mark_time_in(uid, shift_id, ts_dt)
    return jsonify({"msg": "timed in", "timeIn": rec.timeIn.isoformat() if rec.timeIn else None}), 200


@staff_bp.route("/shifts/<int:shift_id>/time-out", methods=["POST"])
@jwt_required()
def api_time_out(shift_id):
    uid = current_user.userId
    sh = db.session.get(Shift, shift_id)
    if not sh:
        return jsonify({"msg": "shift not found"}), 404
    if current_user.type != "admin" and sh.staffId != uid:
        return jsonify({"msg": "forbidden"}), 403

    data = request.get_json() or {}
    ts = data.get("timestamp")
    ts_dt = datetime.fromisoformat(ts) if ts else datetime.utcnow()

    rec = mark_time_out(uid, shift_id, ts_dt)
    return jsonify({"msg": "timed out", "timeOut": rec.timeOut.isoformat() if rec.timeOut else None}), 200


@staff_bp.route("/roster/<int:roster_id>/report", methods=["POST"])
@jwt_required()
def api_generate_report(roster_id):
    if not is_admin(current_user):
        return jsonify({"msg": "admin only"}), 403
    roster = db.session.get(Roster, roster_id)
    if not roster:
        return jsonify({"msg": "roster not found"}), 404
    report = generate_shift_report_for_roster(roster)
    return jsonify({"reportId": report.reportId, "summary": report.summary}), 201
