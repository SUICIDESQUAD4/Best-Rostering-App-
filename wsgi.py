# wsgi.py (add / update inside your project)
import click
from flask.cli import with_appcontext, AppGroup
from datetime import datetime, date, timedelta
from App.main import create_app
from App.database import db
from App.models.user import User
from App.models.admin import Admin
from App.models.staff import Staff
from App.models.roster import Roster
from App.models.shift import Shift
from App.models.attendance import AttendanceRecord
from App.models.shiftreport import ShiftReport

app = create_app()
cli = AppGroup("rostering")

# ---------- helper ----------
def parse_dt(dt_str):
    # Accept ISO formats like 2025-09-29T09:00 or '2025-09-29 09:00'
    try:
        return datetime.fromisoformat(dt_str)
    except Exception:
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")

def parse_date(d_str):
    return date.fromisoformat(d_str)

# ---------- init-db ----------
@cli.command("init-db")
@with_appcontext
def init_db():
    """Initialize DB and seed demo data."""
    db.drop_all()
    db.create_all()

    # Seed admin + staff + roster + shifts
    admin = Admin(username="admin", passwordHash="adminpass", email="admin@example.com", type="admin")
    staff1 = Staff(username="john", passwordHash="pass", email="john@example.com", role="Cashier", type="staff")
    staff2 = Staff(username="jane", passwordHash="pass", email="jane@example.com", role="Cook", type="staff")
    db.session.add_all([admin, staff1, staff2])
    db.session.commit()

    # create roster for next Monday (example week start)
    from datetime import timedelta
    today = date.today()
    # choose a week start = next Monday for demo
    week_start = today
    # ensure monday
    week_start = week_start - timedelta(days=week_start.weekday())
    roster = Roster(weekStartDate=week_start, weekEndDate=week_start + timedelta(days=6))
    db.session.add(roster)
    db.session.commit()

    # sample shift
    s1 = Shift(rosterId=roster.rosterId, staffId=staff1.userId,
               startTime=datetime.combine(week_start, datetime.min.time()).replace(hour=9),
               endTime=datetime.combine(week_start, datetime.min.time()).replace(hour=17))
    db.session.add(s1)
    db.session.commit()

    click.echo("Initialized DB with sample Admin, Staff, Roster, and Shifts.")

# ---------- create-staff ----------
@cli.command("create-staff")
@with_appcontext
@click.argument("username")
@click.argument("email")
@click.argument("password")
@click.argument("role")
def create_staff(username, email, password, role):
    """Create a Staff user."""
    if Staff.query.filter_by(username=username).first():
        click.echo("Username already exists.")
        return
    st = Staff(username=username, passwordHash=password, email=email, role=role, type="staff")
    db.session.add(st)
    db.session.commit()
    click.echo(f"Created staff: {st.userId} - {st.username}")

# ---------- schedule-shift ----------
@cli.command("schedule-shift")
@with_appcontext
@click.argument("staff_id", type=int)
@click.argument("start")
@click.argument("end")
@click.option("--week-start", default=None, help="YYYY-MM-DD (optional roster week start)")
def schedule_shift(staff_id, start, end, week_start):
    """
    Schedule a single shift for a staff member.
    start/end: ISO datetime strings (e.g., 2025-09-29T09:00)
    """
    staff = Staff.query.get(staff_id)
    if not staff:
        click.echo("Staff not found.")
        return
    try:
        start_dt = parse_dt(start)
        end_dt = parse_dt(end)
    except Exception as e:
        click.echo("Invalid date format. Use YYYY-MM-DDTHH:MM")
        return
    # determine roster week
    if week_start:
        try:
            ws = parse_date(week_start)
        except:
            click.echo("Invalid week-start; use YYYY-MM-DD")
            return
    else:
        # compute week start containing start_dt
        ws = (start_dt.date())
        ws = ws - timedelta(days=ws.weekday())

    roster = Roster.get_or_create_by_week(ws)
    # create shift
    shift = Shift(rosterId=roster.rosterId, staffId=staff.userId,
                  startTime=start_dt, endTime=end_dt)
    db.session.add(shift)
    db.session.commit()
    click.echo(f"Scheduled shift {shift.shiftId} for staff {staff.username} on {start_dt.isoformat()} - {end_dt.isoformat()}")

# ---------- schedule-week ----------
@cli.command("schedule-week")
@with_appcontext
@click.argument("staff_id", type=int)
@click.option("--shift", multiple=True, help="Repeatable; 'YYYY-MM-DDTHH:MM,YYYY-MM-DDTHH:MM'")
@click.option("--week-start", required=False, help="YYYY-MM-DD")
def schedule_week(staff_id, shift, week_start):
    """Schedule multiple shifts (week) for a staff member."""
    staff = Staff.query.get(staff_id)
    if not staff:
        click.echo("Staff not found.")
        return
    if not shift:
        click.echo("No shifts provided. Use --shift option multiple times.")
        return
    if week_start:
        ws = parse_date(week_start)
    else:
        # derive from first shift start
        ws = parse_dt(shift[0].split(",")[0]).date()
        ws = ws - timedelta(days=ws.weekday())
    roster = Roster.get_or_create_by_week(ws)
    created = 0
    for s in shift:
        try:
            start_str, end_str = s.split(",")
            st = parse_dt(start_str)
            et = parse_dt(end_str)
        except Exception:
            click.echo(f"Invalid shift format: {s}")
            continue
        new_shift = Shift(rosterId=roster.rosterId, staffId=staff.userId,
                          startTime=st, endTime=et)
        db.session.add(new_shift)
        created += 1
    db.session.commit()
    click.echo(f"Created {created} shifts for staff {staff.username} in week starting {roster.weekStartDate}")

# ---------- view-roster ----------
@cli.command("view-roster")
@with_appcontext
@click.option("--week-start", default=None, help="YYYY-MM-DD (optional)")
def view_roster(week_start):
    """Show combined roster (all shifts) for a week or all."""
    from datetime import timedelta
    if week_start:
        ws = parse_date(week_start)
        roster = Roster.query.filter_by(weekStartDate=ws).first()
        if not roster:
            click.echo("No roster found for that week.")
            return
        shifts = roster.getCombinedRoster()
    else:
        shifts = Shift.query.order_by(Shift.startTime).all()

    if not shifts:
        click.echo("No scheduled shifts.")
        return
    for sh in shifts:
        staff = Staff.query.get(sh.staffId) if sh.staffId else None
        name = staff.username if staff else "UNASSIGNED"
        click.echo(f"Shift {sh.shiftId}: {name} | {sh.startTime} - {sh.endTime}")

# ---------- time-in ----------
@cli.command("time-in")
@with_appcontext
@click.argument("staff_id", type=int)
@click.argument("shift_id", type=int)
@click.option("--timestamp", default=None, help="ISO datetime; default is now")
def time_in(staff_id, shift_id, timestamp):
    """Record time-in for staff for a shift."""
    staff = Staff.query.get(staff_id)
    shift = Shift.query.get(shift_id)
    if not staff or not shift:
        click.echo("Staff or Shift not found.")
        return
    ts = datetime.fromisoformat(timestamp) if timestamp else datetime.utcnow()
    rec = AttendanceRecord.get_or_create(staff_id, shift_id)
    rec.markTimeIn(ts)
    click.echo(f"Marked time-in for staff {staff.username} on shift {shift_id} at {ts}")

# ---------- time-out ----------
@cli.command("time-out")
@with_appcontext
@click.argument("staff_id", type=int)
@click.argument("shift_id", type=int)
@click.option("--timestamp", default=None, help="ISO datetime; default is now")
def time_out(staff_id, shift_id, timestamp):
    """Record time-out for staff for a shift."""
    staff = Staff.query.get(staff_id)
    shift = Shift.query.get(shift_id)
    if not staff or not shift:
        click.echo("Staff or Shift not found.")
        return
    ts = datetime.fromisoformat(timestamp) if timestamp else datetime.utcnow()
    rec = AttendanceRecord.get_or_create(staff_id, shift_id)
    rec.markTimeOut(ts)
    click.echo(f"Marked time-out for staff {staff.username} on shift {shift_id} at {ts}")

# ---------- view-shift-report ----------
@cli.command("view-shift-report")
@with_appcontext
@click.option("--week-start", required=True, help="Week start date YYYY-MM-DD")
def view_shift_report(week_start):
    """Generate and display a simple shift report for the week (Admin)."""
    ws = parse_date(week_start)
    roster = Roster.query.filter_by(weekStartDate=ws).first()
    if not roster:
        click.echo("No roster found for that week.")
        return
    # get attendance for roster shifts
    shifts = roster.getCombinedRoster()
    shift_ids = [s.shiftId for s in shifts]
    attendance = AttendanceRecord.query.filter(AttendanceRecord.shiftId.in_(shift_ids)).all()

    # create & generate report instance
    report = ShiftReport(rosterId=roster.rosterId, weekStartDate=roster.weekStartDate, weekEndDate=roster.weekEndDate)
    db.session.add(report)
    db.session.commit()
    summary = report.generateReport(roster, attendance)
    click.echo(summary)

app.cli.add_command(cli)
# ---------- end of file ----------
