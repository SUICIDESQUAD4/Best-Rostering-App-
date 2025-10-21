import click
from flask.cli import AppGroup, with_appcontext
from datetime import datetime, date, timedelta
import random

from App.controllers import auth_controller, staff_controller
from App.main import create_app
from App.database import db

# Import models
from App.models.user import User
from App.models.admin import Admin
from App.models.staff import Staff
from App.models.roster import Roster
from App.models.shift import Shift
from App.models.attendance import AttendanceRecord
from App.models.shiftreport import ShiftReport

# Flask app
app = create_app()

# CLI groups
system_cli = AppGroup("system", help="System maintenance commands")
admin_cli = AppGroup("admin", help="Admin commands for managing staff and shifts")
staff_cli = AppGroup("staff", help="Staff commands for viewing roster and attendance")

# ---------- Helper functions ----------
def parse_dt(dt_str):
    """Parse datetime string (YYYY-MM-DDTHH:MM)."""
    return datetime.fromisoformat(dt_str)

def parse_date(d_str):
    """Parse date string (YYYY-MM-DD)."""
    return date.fromisoformat(d_str)

# ---------- SYSTEM COMMANDS ----------
@system_cli.command("init-db")
@with_appcontext
def init_db():
    """Initialize database and seed demo data with admins, staff, rosters, shifts, and randomized attendance records."""
    db.drop_all()
    db.create_all()

    # Admins (with hashed passwords)
    admin1 = Admin(username="admin1", email="admin1@example.com", type="admin")
    admin1.set_password("adminpass1")

    admin2 = Admin(username="admin2", email="admin2@example.com", type="admin")
    admin2.set_password("adminpass2")

    # Staff (6 total)
    staff_members = [
        Staff(username="alice", email="alice@example.com", role="Cashier", type="staff"),
        Staff(username="bob", email="bob@example.com", role="Cook", type="staff"),
        Staff(username="carol", email="carol@example.com", role="Waiter", type="staff"),
        Staff(username="dave", email="dave@example.com", role="Cleaner", type="staff"),
        Staff(username="eve", email="eve@example.com", role="Bartender", type="staff"),
        Staff(username="frank", email="frank@example.com", role="Security", type="staff"),
    ]
    default_staff_password = {
        "alice": "alicepass",
        "bob": "bobpass",
        "carol": "carolpass",
        "dave": "davepass",
        "eve": "evepass",
        "frank": "frankpass"
    }
    for s in staff_members:
        s.set_password(default_staff_password[s.username])

    db.session.add_all([admin1, admin2] + staff_members)
    db.session.commit()

    # Create 5 rosters
    today = date.today()
    current_week_start = today - timedelta(days=today.weekday())
    all_rosters = []
    for i in range(5):
        week_start = current_week_start - timedelta(weeks=i)
        roster = Roster(weekStartDate=week_start, weekEndDate=week_start + timedelta(days=6))
        db.session.add(roster)
        all_rosters.append(roster)
    db.session.commit()

    # Shifts & Attendance
    all_shifts = []
    all_attendance = []
    for roster in all_rosters:
        for staff in staff_members:
            day_offset = random.randint(0, 6)
            start_hour = random.randint(8, 14)
            shift_start = datetime.combine(roster.weekStartDate, datetime.min.time()) + timedelta(days=day_offset, hours=start_hour)
            shift_end = shift_start + timedelta(hours=8)

            shift = Shift(rosterId=roster.rosterId, staffId=staff.userId, startTime=shift_start, endTime=shift_end)
            db.session.add(shift)
            db.session.commit()
            all_shifts.append(shift)

            attendance_type = random.choice(["full", "late", "absent", "early_leave"])
            if attendance_type == "full":
                time_in = shift_start + timedelta(minutes=random.randint(0, 10))
                time_out = shift_end - timedelta(minutes=random.randint(0, 10))
            elif attendance_type == "late":
                time_in = shift_start + timedelta(minutes=random.randint(15, 60))
                time_out = shift_end - timedelta(minutes=random.randint(0, 10))
            elif attendance_type == "early_leave":
                time_in = shift_start + timedelta(minutes=random.randint(0, 10))
                time_out = shift_end - timedelta(hours=random.randint(1, 3))
            else:
                time_in = None
                time_out = None

            record = AttendanceRecord(staffId=staff.userId, shiftId=shift.shiftId, timeIn=time_in, timeOut=time_out)
            db.session.add(record)
            all_attendance.append(record)
    db.session.commit()

    print("✅ Database initialized with:")
    print(" - 2 Admins (with hashed passwords)")
    print(" - 6 Staff (with hashed passwords)")
    print(" - 5 Rosters (current + 4 past weeks)")
    print(f" - {len(all_shifts)} Shifts (randomized)")
    print(f" - {len(all_attendance)} Attendance Records (varied & randomized)")

@system_cli.command("rollback-db")
@with_appcontext
def rollback_db():
    """Rollback uncommitted database changes."""
    db.session.rollback()
    print("🔁 Rolled back uncommitted changes.")

# ---------- ADMIN COMMANDS ----------
@admin_cli.command("add-staff")
@with_appcontext
def add_staff():
    """Add a new staff member interactively."""
    username = input("Enter staff username: ")
    email = input("Enter staff email: ")
    password = input("Enter staff password: ")
    role = input("Enter staff role: ")

    staff = Staff(username=username, email=email, role=role, type="staff")
    staff.set_password(password)
    db.session.add(staff)
    db.session.commit()
    print(f"✅ Added staff {staff.username} with ID {staff.userId}")

@admin_cli.command("delete-staff")
@with_appcontext
@click.argument("staff_id", type=int)
def delete_staff(staff_id):
    staff = Staff.query.get(staff_id)
    if not staff:
        print("⚠️ Staff not found.")
        return
    db.session.delete(staff)
    db.session.commit()
    print(f"🗑️ Deleted staff with ID {staff_id}")

@admin_cli.command("list-staff")
@with_appcontext
def list_staff():
    staff_members = Staff.query.all()
    if not staff_members:
        print("⚠️ No staff found.")
        return
    for s in staff_members:
        print(f"{s.userId}: {s.username} ({s.role})")

@admin_cli.command("schedule-shift")
@with_appcontext
@click.option("--staff-id", type=int, help="Staff ID")
@click.option("--start", type=str, help="Start time (YYYY-MM-DDTHH:MM)")
@click.option("--end", type=str, help="End time (YYYY-MM-DDTHH:MM)")
def schedule_shift(staff_id, start, end):
    """Schedule a shift for a staff."""
    if not staff_id:
        staff_id = click.prompt("Enter Staff ID", type=int)
    if not start:
        start = click.prompt("Enter start datetime (YYYY-MM-DDTHH:MM)")
    if not end:
        end = click.prompt("Enter end datetime (YYYY-MM-DDTHH:MM)")

    start_dt = parse_dt(start)
    end_dt = parse_dt(end)

    # use current week's roster
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    roster = Roster.query.filter_by(weekStartDate=week_start).first()
    if not roster:
        roster = Roster(weekStartDate=week_start, weekEndDate=week_start + timedelta(days=6))
        db.session.add(roster)
        db.session.commit()

    new_shift = Shift(staffId=staff_id, startTime=start_dt, endTime=end_dt, rosterId=roster.rosterId)
    db.session.add(new_shift)
    db.session.commit()
    print(f"✅ Shift scheduled for staff {staff_id}: {start_dt} → {end_dt}")

@admin_cli.command("list-shifts")
@with_appcontext
def list_shifts():
    """List all scheduled shifts."""
    shifts = Shift.query.all()
    if not shifts:
        print("⚠️ No shifts found.")
        return
    for sh in shifts:
        s = Staff.query.get(sh.staffId)
        name = s.username if s else "Unknown"
        print(f"Shift {sh.shiftId}: Staff {name} | {sh.startTime} - {sh.endTime}")

@admin_cli.command("view-shift-report")
@with_appcontext
def view_shift_report():
    """
    Generate and view a weekly shift report.

    Interactive mode:
      - Lists all existing rosters (by week start date).
      - Prompts you to choose which roster to generate a report for.
      - Displays shift details, per-staff summaries, and overall totals.
      - Saves the report summary into the ShiftReport table.
    """
    rosters = Roster.query.order_by(Roster.weekStartDate).all()
    if not rosters:
        print("No rosters found. Please schedule shifts first.")
        return

    print("\nAvailable Rosters:")
    for idx, r in enumerate(rosters, start=1):
        print(f"[{idx}] {r.weekStartDate} → {r.weekEndDate}")

    # ask the user to choose one
    choice = input("\nEnter the number of the roster you want a report for: ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(rosters):
        print("Invalid selection. Aborting.")
        return

    roster = rosters[int(choice) - 1]

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

    # print to console
    print("\n" + final_summary)
    print("\nReport saved to database.")

# ---------- STAFF COMMANDS ----------
@staff_cli.command("view-roster")
@with_appcontext
@click.option("--week-start", default=None, help="Week start date (YYYY-MM-DD)")
def view_roster(week_start):
    if week_start:
        ws = parse_date(week_start)
        roster = Roster.query.filter_by(weekStartDate=ws).first()
        if not roster:
            print("⚠️ No roster found for that week.")
            return
        shifts = roster.getCombinedRoster()
    else:
        shifts = Shift.query.order_by(Shift.startTime).all()

    for sh in shifts:
        staff = Staff.query.get(sh.staffId)
        name = staff.username if staff else "UNASSIGNED"
        print(f"Shift {sh.shiftId}: {name} | {sh.startTime} - {sh.endTime}")

@staff_cli.command("time-in")
@with_appcontext
@click.argument("staff_id", type=int)
@click.argument("shift_id", type=int)
@click.option("--timestamp", default=None)
def time_in(staff_id, shift_id, timestamp):
    ts = datetime.fromisoformat(timestamp) if timestamp else datetime.utcnow()
    rec = AttendanceRecord.get_or_create(staff_id, shift_id)
    rec.markTimeIn(ts)
    print(f"⏰ Staff {staff_id} timed in for shift {shift_id} at {ts}")

@staff_cli.command("time-out")
@with_appcontext
@click.argument("staff_id", type=int)
@click.argument("shift_id", type=int)
@click.option("--timestamp", default=None)
def time_out(staff_id, shift_id, timestamp):
    ts = datetime.fromisoformat(timestamp) if timestamp else datetime.utcnow()
    rec = AttendanceRecord.get_or_create(staff_id, shift_id)
    rec.markTimeOut(ts)
    print(f"🏁 Staff {staff_id} timed out for shift {shift_id} at {ts}")

@staff_cli.command("view-my-info")
@with_appcontext
@click.argument("staff_id", type=int)
def view_my_info(staff_id):
    staff = Staff.query.get(staff_id)
    if not staff:
        print("⚠️ Staff not found.")
        return
    print(f"👤 ID: {staff.userId}\nUsername: {staff.username}\nEmail: {staff.email}\nRole: {staff.role}")

@staff_cli.command("view-my-shifts")
@with_appcontext
@click.argument("staff_id", type=int)
def view_my_shifts(staff_id):
    shifts = Shift.query.filter_by(staffId=staff_id).order_by(Shift.startTime).all()
    if not shifts:
        print("⚠️ No shifts found for this staff.")
        return
    for sh in shifts:
        print(f"Shift {sh.shiftId}: {sh.startTime} - {sh.endTime}")


# ---------- TEST COMMANDS ----------
import sys
import pytest

test = AppGroup('test', help='Run application tests')

@test.command("unit", help="Run all unit tests")
def run_unit_tests():
    sys.exit(pytest.main(["-k", "UserUnitTests"]))

@test.command("integration", help="Run all integration tests")
def run_integration_tests():
    sys.exit(pytest.main(["-k", "IntegrationTests"]))

@test.command("all", help="Run all tests")
def run_all_tests():
    sys.exit(pytest.main(["-v"]))


# ---------- Register CLI groups ----------
app.cli.add_command(system_cli)
app.cli.add_command(admin_cli)
app.cli.add_command(staff_cli)
app.cli.add_command(test)