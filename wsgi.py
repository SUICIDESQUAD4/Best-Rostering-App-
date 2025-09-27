import click
from flask.cli import AppGroup, with_appcontext
from datetime import datetime, date, timedelta

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
    """Initialize database and seed demo data."""
    db.drop_all()
    db.create_all()

    # Admins
    admin1 = Admin(username="admin1", passwordHash="adminpass1", email="admin1@example.com", type="admin")
    admin2 = Admin(username="admin2", passwordHash="adminpass2", email="admin2@example.com", type="admin")

    # Staff (6 total)
    staff_members = [
        Staff(username="alice", passwordHash="pass", email="alice@example.com", role="Cashier", type="staff"),
        Staff(username="bob", passwordHash="pass", email="bob@example.com", role="Cook", type="staff"),
        Staff(username="carol", passwordHash="pass", email="carol@example.com", role="Waiter", type="staff"),
        Staff(username="dave", passwordHash="pass", email="dave@example.com", role="Cleaner", type="staff"),
        Staff(username="eve", passwordHash="pass", email="eve@example.com", role="Bartender", type="staff"),
        Staff(username="frank", passwordHash="pass", email="frank@example.com", role="Security", type="staff"),
    ]

    # Roster for current week
    week_start = date.today() - timedelta(days=date.today().weekday())
    roster = Roster(weekStartDate=week_start, weekEndDate=week_start + timedelta(days=6))

    # Example shifts
    shift1 = Shift(rosterId=1, staffId=1, startTime=datetime.now(), endTime=datetime.now() + timedelta(hours=8))
    shift2 = Shift(rosterId=1, staffId=2, startTime=datetime.now() + timedelta(days=1), endTime=datetime.now() + timedelta(days=1, hours=8))
    shift3 = Shift(rosterId=1, staffId=3, startTime=datetime.now() + timedelta(days=2), endTime=datetime.now() + timedelta(days=2, hours=8))

    db.session.add_all([admin1, admin2] + staff_members + [roster, shift1, shift2, shift3])
    db.session.commit()

    print("✅ Database initialized with:")
    print(" - 2 Admins")
    print(" - 6 Staff")
    print(" - 1 Roster (this week)")
    print(" - 3 Example Shifts")


@system_cli.command("rollback-db")
@with_appcontext
def rollback_db():
    """Rollback uncommitted database changes."""
    db.session.rollback()
    print("🔄 Rolled back uncommitted changes.")


# ---------- ADMIN COMMANDS ----------
@admin_cli.command("add-staff")
@with_appcontext
def add_staff():
    """Add a new staff member interactively."""
    username = input("Enter staff username: ")
    email = input("Enter staff email: ")
    password = input("Enter staff password: ")
    role = input("Enter staff role: ")

    staff = Staff(username=username, passwordHash=password, email=email, role=role, type="staff")
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
        print("❌ Staff not found.")
        return
    db.session.delete(staff)
    db.session.commit()
    print(f"🗑 Deleted staff with ID {staff_id}")


@admin_cli.command("list-staff")
@with_appcontext
def list_staff():
    """List all staff members."""
    staff_members = Staff.query.all()
    if not staff_members:
        print("No staff found.")
        return
    for s in staff_members:
        print(f"👤 {s.userId}: {s.username} ({s.role})")


@admin_cli.command("schedule-shift")
@with_appcontext
@click.argument("staff_id", type=int)
@click.argument("start")
@click.argument("end")
@click.option("--week-start", default=None, help="Week start date (YYYY-MM-DD)")
def schedule_shift(staff_id, start, end, week_start):
    """Schedule a shift for a staff member."""
    staff = Staff.query.get(staff_id)
    if not staff:
        print("❌ Staff not found.")
        return

    start_dt = parse_dt(start)
    end_dt = parse_dt(end)
    ws = parse_date(week_start) if week_start else start_dt.date() - timedelta(days=start_dt.weekday())
    roster = Roster.query.filter_by(weekStartDate=ws).first()
    if not roster:
        roster = Roster(weekStartDate=ws, weekEndDate=ws + timedelta(days=6))
        db.session.add(roster)
        db.session.commit()

    shift = Shift(rosterId=roster.rosterId, staffId=staff.userId, startTime=start_dt, endTime=end_dt)
    db.session.add(shift)
    db.session.commit()
    print(f"✅ Scheduled shift {shift.shiftId} for staff {staff.username}")


@admin_cli.command("list-shifts")
@with_appcontext
def list_shifts():
    """List all scheduled shifts."""
    shifts = Shift.query.all()
    if not shifts:
        print("No shifts found.")
        return
    for sh in shifts:
        staff = Staff.query.get(sh.staffId)
        staff_name = staff.username if staff else "UNASSIGNED"
        print(f"🕒 Shift {sh.shiftId}: {staff_name} | {sh.startTime} - {sh.endTime}")


@admin_cli.command("view-shift-report")
@with_appcontext
@click.option("--week-start", required=True, help="Week start date (YYYY-MM-DD)")
def view_shift_report(week_start):
    """Generate and view weekly shift report."""
    ws = parse_date(week_start)
    roster = Roster.query.filter_by(weekStartDate=ws).first()
    if not roster:
        print("❌ No roster found for that week.")
        return

    shifts = roster.getCombinedRoster()
    shift_ids = [s.shiftId for s in shifts]
    attendance = AttendanceRecord.query.filter(AttendanceRecord.shiftId.in_(shift_ids)).all()

    report = ShiftReport(rosterId=roster.rosterId, weekStartDate=roster.weekStartDate, weekEndDate=roster.weekEndDate)
    db.session.add(report)
    db.session.commit()

    summary = report.generateReport(roster, attendance)
    print(f"📊 Shift Report ({week_start}): {summary}")


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
            print("❌ No roster found for that week.")
            return
        shifts = roster.getCombinedRoster()
    else:
        shifts = Shift.query.order_by(Shift.startTime).all()

    for sh in shifts:
        staff = Staff.query.get(sh.staffId)
        staff_name = staff.username if staff else "UNASSIGNED"
        print(f"🕒 Shift {sh.shiftId}: {staff_name} | {sh.startTime} - {sh.endTime}")


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
    print(f"✅ Staff {staff_id} timed in for shift {shift_id} at {ts}")


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
    print(f"✅ Staff {staff_id} timed out for shift {shift_id} at {ts}")


# ---------- Register CLI groups ----------
app.cli.add_command(system_cli)
app.cli.add_command(admin_cli)
app.cli.add_command(staff_cli)
