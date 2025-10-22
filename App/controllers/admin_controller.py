# App/controllers/admin_controller.py
from App.database import db
from App.models.staff import Staff
from App.models.shift import Shift
from App.models.roster import Roster
from App.models.shiftreport import ShiftReport
from datetime import datetime, date, timedelta

def list_staff():
    return [s.get_json() for s in Staff.query.all()]

def create_staff(data):
    staff = Staff(
        username=data.get("username"),
        email=data.get("email"),
        role=data.get("role"),
        type="staff"
    )
    staff.set_password(data.get("password"))
    db.session.add(staff)
    db.session.commit()
    return staff.get_json()

def delete_staff(staff_id):
    staff = Staff.query.get(staff_id)
    if not staff:
        return False
    db.session.delete(staff)
    db.session.commit()
    return True

def schedule_shift(data):
    staff_id = data.get("staffId")
    start = datetime.fromisoformat(data.get("start"))
    end = datetime.fromisoformat(data.get("end"))

    # ensure current week roster exists
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    roster = Roster.query.filter_by(weekStartDate=week_start).first()
    if not roster:
        roster = Roster(weekStartDate=week_start, weekEndDate=week_start + timedelta(days=6))
        db.session.add(roster)
        db.session.commit()

    shift = Shift(staffId=staff_id, startTime=start, endTime=end, rosterId=roster.rosterId)
    db.session.add(shift)
    db.session.commit()
    return shift.get_json()

def list_shifts():
    return [s.get_json() for s in Shift.query.all()]

def generate_shift_report(roster_id):
    roster = Roster.query.get(roster_id)
    if not roster:
        return {"error": "Roster not found"}

    summary = f"Report for {roster.weekStartDate} → {roster.weekEndDate}"
    report = ShiftReport(
        rosterId=roster.rosterId,
        weekStartDate=roster.weekStartDate,
        weekEndDate=roster.weekEndDate,
        summary=summary
    )
    db.session.add(report)
    db.session.commit()
    return report.get_json()
