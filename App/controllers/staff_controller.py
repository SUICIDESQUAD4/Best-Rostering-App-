# App/controllers/staff_controller.py
from App.database import db
from App.models.staff import Staff
from App.models.shift import Shift
from App.models.roster import Roster
from App.models.attendance import AttendanceRecord
from datetime import datetime, date, timedelta

def get_profile(staff_id):
    staff = Staff.query.get(staff_id)
    return staff.get_json() if staff else {"error": "Staff not found"}

def view_roster(week_start):
    if week_start:
        ws = date.fromisoformat(week_start)
        roster = Roster.query.filter_by(weekStartDate=ws).first()
    else:
        today = date.today()
        ws = today - timedelta(days=today.weekday())
        roster = Roster.query.filter_by(weekStartDate=ws).first()

    if not roster:
        return {"error": "No roster found"}
    return roster.get_json()

def view_my_shifts(staff_id):
    shifts = Shift.query.filter_by(staffId=staff_id).order_by(Shift.startTime).all()
    return [s.get_json() for s in shifts]

def time_in(staff_id, shift_id, timestamp):
    ts = datetime.fromisoformat(timestamp) if timestamp else datetime.utcnow()
    record = AttendanceRecord.get_or_create(staff_id, shift_id)
    record.markTimeIn(ts)
    db.session.commit()
    return {"message": "Timed in", "timeIn": ts.isoformat()}

def time_out(staff_id, shift_id, timestamp):
    ts = datetime.fromisoformat(timestamp) if timestamp else datetime.utcnow()
    record = AttendanceRecord.get_or_create(staff_id, shift_id)
    record.markTimeOut(ts)
    db.session.commit()
    return {"message": "Timed out", "timeOut": ts.isoformat()}
