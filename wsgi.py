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

    # Set hashed passwords for each staff
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

    # Create 5 rosters (current week + 4 past weeks)
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
            # Random day and hour
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
    """Add a new staff member interactively (password hashed)."""
    username = input("Enter staff username: ")
    email = input("Enter staff email: ")
    password = input("Enter staff password: ")
    role = input("Enter staff role: ")

    staff = Staff(username=username, email=email, role=role, type="staff")
    staff.set_password(password)  # ✅ Hash password
    db.session.add(staff)
    db.session.commit()
    print(f"✅ Added staff {staff.username} with ID {staff.userId}")

@admin_cli.command("delete-staff")
@with_appcontext
@click.argument("staff_id", type=int)
def delete_staff(staff_id):
    """Delete a staff member by ID."""
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
    """List all staff members."""
    staff_members = Staff.query.all()
    if not staff_members:
        print("⚠️ No staff found.")
        return
    for s in staff_members:
        print(f"{s.userId}: {s.username} ({s.role})")

# (Keep your schedule-shift and view-shift-report commands as you have them — no hash changes needed there)

# ---------- STAFF COMMANDS ----------
@staff_cli.command("view-roster")
@with_appcontext
@click.option("--week-start", default=None, help="Week start date (YYYY-MM-DD)")
def view_roster(week_start):
    """View combined roster for the week."""
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
        staff_name = staff.username if staff else "UNASSIGNED"
        print(f"Shift {sh.shiftId}: {staff_name} | {sh.startTime} - {sh.endTime}")

@staff_cli.command("time-in")
@with_appcontext
@click.argument("staff_id", type=int)
@click.argument("shift_id", type=int)
@click.option("--timestamp", default=None, help="Optional timestamp (YYYY-MM-DDTHH:MM)")
def time_in(staff_id, shift_id, timestamp):
    """Record time in for a shift."""
    ts = datetime.fromisoformat(timestamp) if timestamp else datetime.utcnow()
    rec = AttendanceRecord.get_or_create(staff_id, shift_id)
    rec.markTimeIn(ts)
    print(f"⏰ Staff {staff_id} timed in for shift {shift_id} at {ts}")

@staff_cli.command("time-out")
@with_appcontext
@click.argument("staff_id", type=int)
@click.argument("shift_id", type=int)
@click.option("--timestamp", default=None, help="Optional timestamp (YYYY-MM-DDTHH:MM)")
def time_out(staff_id, shift_id, timestamp):
    """Record time out for a shift."""
    ts = datetime.fromisoformat(timestamp) if timestamp else datetime.utcnow()
    rec = AttendanceRecord.get_or_create(staff_id, shift_id)
    rec.markTimeOut(ts)
    print(f"🏁 Staff {staff_id} timed out for shift {shift_id} at {ts}")

# ---------- Register CLI groups ----------
app.cli.add_command(system_cli)
app.cli.add_command(admin_cli)
app.cli.add_command(staff_cli)
