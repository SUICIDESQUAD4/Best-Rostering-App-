# App/controllers/staff_controller.py
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta

from App.database import db
from App.models.staff import Staff
from App.models.shift import Shift
from App.models.roster import Roster
from App.models.attendance import AttendanceRecord
from App.models.shiftreport import ShiftReport

def list_staff() -> List[Dict[str, Any]]:
    staff = db.session.scalars(db.select(Staff)).all()
    return [s.to_dict() for s in staff]

def get_staff(staff_id: int) -> Optional[Staff]:
    return db.session.get(Staff, staff_id)

def create_staff(username: str, password: str, email: str, role: str) -> Staff:
    # Create both User and Staff record (polymorphic)
    # We instantiate Staff so polymorphic identity is correct
    staff = Staff(username=username, email=email, role=role, type="staff", passwordHash="")
    staff.set_password(password)
    db.session.add(staff)
    db.session.commit()
    return staff

def update_staff(staff_id: int, **updates) -> Optional[Staff]:
    staff = get_staff(staff_id)
    if not staff:
        return None
    if "username" in updates:
        staff.username = updates["username"]
    if "email" in updates:
        staff.email = updates["email"]
    if "role" in updates:
        staff.role = updates["role"]
    if "password" in updates:
        staff.set_password(updates["password"])
    db.session.commit()
    return staff

def delete_staff(staff_id: int) -> bool:
    staff = get_staff(staff_id)
    if not staff:
        return False
    db.session.delete(staff)
    db.session.commit()
    return True

def get_current_roster() -> Optional[Roster]:
    """
    Return the roster for the current week (starting Monday).
    """
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    roster = db.session.scalars(db.select(Roster).filter_by(weekStartDate=week_start)).first()
    return roster

def get_roster_by_weekstart(week_start: date) -> Optional[Roster]:
    roster = db.session.scalars(db.select(Roster).filter_by(weekStartDate=week_start)).first()
    return roster

def schedule_shift_for_staff(staff_id: int, start: datetime, end: datetime, week_start: Optional[date] = None) -> Shift:
    staff = get_staff(staff_id)
    if not staff:
        raise ValueError("Staff not found")

    if week_start is None:
        week_start = start.date() - timedelta(days=start.date().weekday())

    roster = db.session.scalars(db.select(Roster).filter_by(weekStartDate=week_start)).first()
    if not roster:
        roster = Roster(weekStartDate=week_start, weekEndDate=week_start + timedelta(days=6))
        db.session.add(roster)
        db.session.flush()

    # optional overlap check omitted for brevity
    shift = Shift(rosterId=roster.rosterId, staffId=staff.userId, startTime=start, endTime=end)
    db.session.add(shift)
    db.session.commit()
    return shift

def mark_time_in(staff_id: int, shift_id: int, timestamp: Optional[datetime] = None) -> AttendanceRecord:
    if timestamp is None:
        timestamp = datetime.utcnow()
    rec = AttendanceRecord.get_or_create(staff_id, shift_id)
    rec.timeIn = timestamp
    db.session.commit()
    return rec

def mark_time_out(staff_id: int, shift_id: int, timestamp: Optional[datetime] = None) -> AttendanceRecord:
    if timestamp is None:
        timestamp = datetime.utcnow()
    rec = AttendanceRecord.get_or_create(staff_id, shift_id)
    rec.timeOut = timestamp
    db.session.commit()
    return rec

def generate_shift_report_for_roster(roster: Roster) -> ShiftReport:
    shifts = roster.getCombinedRoster()
    shift_ids = [s.shiftId for s in shifts]
    attendance = db.session.scalars(db.select(AttendanceRecord).filter(AttendanceRecord.shiftId.in_(shift_ids))).all()

    report = ShiftReport(rosterId=roster.rosterId, weekStartDate=roster.weekStartDate, weekEndDate=roster.weekEndDate)
    db.session.add(report)
    db.session.flush()

    # Build the summary similar to prior implementation
    staff_hours = {}
    total_shifts = 0
    total_hours = 0.0
    lines = []
    lines.append("Shift Report")
    lines.append("+--------------------------------------+")
    lines.append(f" Week: {roster.weekStartDate} → {roster.weekEndDate}")
    lines.append("+--------------------------------------+\n")

    for rec in attendance:
        s = db.session.get(Staff, rec.staffId)
        sh = db.session.get(Shift, rec.shiftId)
        staff_name = s.username if s else "Unknown"
        time_in = rec.timeIn.strftime("%Y-%m-%d %H:%M") if rec.timeIn else "N/A"
        time_out = rec.timeOut.strftime("%Y-%m-%d %H:%M") if rec.timeOut else "N/A"
        if rec.timeIn and rec.timeOut:
            hours = (rec.timeOut - rec.timeIn).total_seconds() / 3600
        else:
            hours = 0.0
        staff_hours[staff_name] = staff_hours.get(staff_name, 0.0) + hours
        total_shifts += 1
        total_hours += hours

        lines.append(f"Staff: {staff_name}")
        lines.append(f" Shift: {sh.startTime} → {sh.endTime}")
        lines.append(f" Time In: {time_in} | Time Out: {time_out}")
        lines.append(f" Hours Worked: {hours:.2f}")
        lines.append("----------------------------------------")

    lines.append("\nSummary of Hours Worked (per staff):")
    for name, hrs in staff_hours.items():
        lines.append(f" {name}: {hrs:.2f} hrs")

    lines.append("\nOverall Summary:")
    lines.append(f" Total Shifts: {total_shifts}")
    lines.append(f" Total Staff: {len(staff_hours)}")
    lines.append(f" Total Hours Worked: {total_hours:.2f} hrs")

    report.summary = "\n".join(lines)
    db.session.commit()
    return report
