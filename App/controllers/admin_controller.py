# App/controllers/admin_controller.py
from App.database import db
from App.models.staff import Staff
from App.models.shift import Shift
from App.models.roster import Roster
from App.models.shiftreport import ShiftReport
from datetime import datetime, date, timedelta
from datetime import datetime, date, timedelta
from App.database import db

from flask import Response

# Import models
from App.models.staff import Staff
from App.models.roster import Roster
from App.models.shift import Shift
from App.models.attendance import AttendanceRecord
from App.models.shiftreport import ShiftReport



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
    
    # collect data
    shifts = roster.getCombinedRoster()
    shift_ids = [s.shiftId for s in shifts]
    attendance_records = AttendanceRecord.query.filter(
        AttendanceRecord.shiftId.in_(shift_ids)
    ).all()

    # tracking totals
    staff_hours = {}
    total_shifts = 0
    total_hours = 0.0

    # start building a summary string to save
    summary_lines = []
    summary_lines.append("Shift Report")
    summary_lines.append("+--------------------------------------+")
    summary_lines.append(f" Week: {roster.weekStartDate} → {roster.weekEndDate}")
    summary_lines.append("+--------------------------------------+\n")

    for record in attendance_records:
        staff = Staff.query.get(record.staffId)
        shift = Shift.query.get(record.shiftId)

        staff_name = staff.username if staff else "Unknown Staff"
        shift_info = f"{shift.startTime} → {shift.endTime}" if shift else "No shift info"
        time_in = record.timeIn.strftime("%Y-%m-%d %H:%M") if record.timeIn else "N/A"
        time_out = record.timeOut.strftime("%Y-%m-%d %H:%M") if record.timeOut else "N/A"

        if record.timeIn and record.timeOut:
            hours_worked = (record.timeOut - record.timeIn).total_seconds() / 3600
            hours_text = f"{hours_worked:.2f} hrs"
        else:
            hours_worked = 0
            hours_text = "Incomplete (No time in/out)"

        # accumulate totals
        staff_hours[staff_name] = staff_hours.get(staff_name, 0) + hours_worked
        total_shifts += 1
        total_hours += hours_worked

        # add to summary string
        summary_lines.append(f"Staff: {staff_name}")
        summary_lines.append(f" Shift: {shift_info}")
        summary_lines.append(f" Time In: {time_in} | Time Out: {time_out}")
        summary_lines.append(f" Hours Worked: {hours_text}")
        summary_lines.append("----------------------------------------")

    # per-staff summary
    summary_lines.append("\nSummary of Hours Worked (per staff):")
    for name, hrs in staff_hours.items():
        summary_lines.append(f" {name}: {hrs:.2f} hrs")

    # overall summary
    summary_lines.append("\nOverall Summary:")
    summary_lines.append(f" Total Shifts: {total_shifts}")
    summary_lines.append(f" Total Staff: {len(staff_hours)}")
    summary_lines.append(f" Total Hours Worked: {total_hours:.2f} hrs")

    # join all summary lines
    final_summary = "\n".join(summary_lines)

    # save to DB
    report = ShiftReport(
        rosterId=roster.rosterId,
        weekStartDate=roster.weekStartDate,
        weekEndDate=roster.weekEndDate,
        summary=final_summary
    )
    
    db.session.add(report)
    db.session.commit()
    
    return Response(final_summary, mimetype='text/plain')

    # return {
    #     "status": "success",
    #     "rosterId": roster.rosterId,
    #     "weekStartDate": str(roster.weekStartDate),
    #     "weekEndDate": str(roster.weekEndDate),
    #     "summary": final_summary
    # }
