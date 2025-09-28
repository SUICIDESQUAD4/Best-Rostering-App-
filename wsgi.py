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
import random

@system_cli.command("init-db")
@with_appcontext
def init_db():
    """Initialize database and seed demo data with admins, staff, rosters, shifts, and randomized attendance records."""
    db.drop_all()
    db.create_all()

    # Admins
    admin1 = Admin(username="admin1", passwordHash="adminpass1", email="admin1@example.com", type="admin")
    admin2 = Admin(username="admin2", passwordHash="adminpass2", email="admin2@example.com", type="admin")

    # Staff (6 total)
    staff_members = [
        Staff(username="alice", passwordHash="alicepass", email="alice@example.com", role="Cashier", type="staff"),
        Staff(username="bob", passwordHash="bobpass", email="bob@example.com", role="Cook", type="staff"),
        Staff(username="carol", passwordHash="carolpass", email="carol@example.com", role="Waiter", type="staff"),
        Staff(username="dave", passwordHash="davepass", email="dave@example.com", role="Cleaner", type="staff"),
        Staff(username="eve", passwordHash="evepass", email="eve@example.com", role="Bartender", type="staff"),
        Staff(username="frank", passwordHash="frankpass", email="frank@example.com", role="Security", type="staff"),
    ]

    db.session.add_all([admin1, admin2] + staff_members)
    db.session.commit()

    # Create 5 rosters (current week + 4 past weeks)
    today = date.today()
    current_week_start = today - timedelta(days=today.weekday())

    all_rosters = []
    for i in range(5):
        week_start = current_week_start - timedelta(weeks=i)
        roster = Roster(
            weekStartDate=week_start,
            weekEndDate=week_start + timedelta(days=6)
        )
        db.session.add(roster)
        all_rosters.append(roster)
    db.session.commit()

    # Example Shifts & Attendance for each roster
    all_shifts = []
    all_attendance = []

    for roster in all_rosters:
        for staff in staff_members:
            # Random day of week (0=Mon, 6=Sun)
            day_offset = random.randint(0, 6)

            # Random start hour between 8 AM and 2 PM
            start_hour = random.randint(8, 14)

            shift_start = datetime.combine(roster.weekStartDate, datetime.min.time()) + timedelta(days=day_offset, hours=start_hour)
            shift_end = shift_start + timedelta(hours=8)

            shift = Shift(
                rosterId=roster.rosterId,
                staffId=staff.userId,
                startTime=shift_start,
                endTime=shift_end
            )
            db.session.add(shift)
            db.session.commit()  # get shiftId

            all_shifts.append(shift)

            # Attendance variations
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
            else:  # absent
                time_in = None
                time_out = None

            record = AttendanceRecord(
                staffId=staff.userId,
                shiftId=shift.shiftId,
                timeIn=time_in,
                timeOut=time_out
            )
            db.session.add(record)
            all_attendance.append(record)

    db.session.commit()

    print("Database initialized with:")
    print(" - 2 Admins")
    print(" - 6 Staff")
    print(" - 5 Rosters (current + 4 past weeks)")
    print(f" - {len(all_shifts)} Shifts (about 6 per week, randomized)")
    print(f" - {len(all_attendance)} Attendance Records (varied & randomized)")




@system_cli.command("rollback-db")
@with_appcontext
def rollback_db():
    """Rollback uncommitted database changes."""
    db.session.rollback()
    print("Rolled back uncommitted changes.")


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
    print(f"Added staff {staff.username} with ID {staff.userId}")


@admin_cli.command("delete-staff")
@with_appcontext
@click.argument("staff_id", type=int)
def delete_staff(staff_id):
    """Delete a staff member by ID."""
    staff = Staff.query.get(staff_id)
    if not staff:
        print("Staff not found.")
        return
    db.session.delete(staff)
    db.session.commit()
    print(f"Deleted staff with ID {staff_id}")


@admin_cli.command("list-staff")
@with_appcontext
def list_staff():
    """List all staff members."""
    staff_members = Staff.query.all()
    if not staff_members:
        print("No staff found.")
        return
    for s in staff_members:
        print(f"{s.userId}: {s.username} ({s.role})")


@admin_cli.command("schedule-shift")
@with_appcontext
@click.option("--staff-id", type=int, help="Staff ID (optional). If omitted you will be prompted.")
@click.option("--start", help="Start datetime (optional) - format: YYYY-MM-DDTHH:MM (e.g. 2025-09-29T09:00)")
@click.option("--end", help="End datetime (optional) - format: YYYY-MM-DDTHH:MM (e.g. 2025-09-29T17:00)")
@click.option("--week-start", default=None, help="Optional roster week-start date (YYYY-MM-DD). If omitted it will be derived.")
def schedule_shift(staff_id, start, end, week_start):
    """
    Schedule shift(s) for a staff member.

    Two modes:
    1) Non-interactive:
       flask admin schedule-shift --staff-id 2 --start 2025-09-29T09:00 --end 2025-09-29T17:00
    2) Interactive (recommended when you want step-by-step input):
       flask admin schedule-shift
       - will prompt you for staff, then allow you to enter one or more shifts interactively.

    Date/time format: YYYY-MM-DDTHH:MM (example: 2025-09-29T09:00)
    Week-start format: YYYY-MM-DD (example: 2025-09-29)
    """
    # Helper for overlap check
    def has_overlap(staff_id, new_start, new_end):
        from sqlalchemy import and_, or_
        # any existing shift for staff that overlaps the new shift?
        existing = Shift.query.filter(Shift.staffId == staff_id).all()
        for ex in existing:
            if (new_start < ex.endTime) and (new_end > ex.startTime):
                return ex
        return None

    # If staff_id not provided, show staff list and prompt the user
    if not staff_id:
        print("\nNo staff id provided. Here are existing staff members:\n")
        staff_members = Staff.query.all()
        if not staff_members:
            print("No staff records found. Use 'flask admin add-staff' first.")
            return
        for s in staff_members:
            print(f"  ID {s.userId}  - {s.username} ({s.role})")
        while True:
            raw = input("\nEnter staff ID to schedule (or 'q' to quit): ").strip()
            if raw.lower() == "q":
                print("Cancelled.")
                return
            if raw.isdigit():
                staff_id = int(raw)
                staff = Staff.query.get(staff_id)
                if not staff:
                    print("Invalid staff ID — try again.")
                    continue
                break
            print("Please enter a numeric staff ID.")

    staff = Staff.query.get(staff_id)
    if not staff:
        print(f"Staff with ID {staff_id} not found.")
        return

    # If both start and end passed -> do single non-interactive scheduling (but still confirm)
    if start and end:
        try:
            start_dt = parse_dt(start)
            end_dt = parse_dt(end)
        except Exception as e:
            print("Error: Invalid datetime format. Use YYYY-MM-DDTHH:MM (e.g. 2025-09-29T09:00).")
            return

        if start_dt >= end_dt:
            print("Error: start must be before end.")
            return

        # Determine roster week start
        if week_start:
            try:
                ws = parse_date(week_start)
            except Exception:
                print("Error: Invalid week-start format. Use YYYY-MM-DD.")
                return
        else:
            ws = start_dt.date() - timedelta(days=start_dt.weekday())

        try:
            # create or get roster
            roster = Roster.query.filter_by(weekStartDate=ws).first()
            if not roster:
                roster = Roster(weekStartDate=ws, weekEndDate=ws + timedelta(days=6))
                db.session.add(roster)
                db.session.commit()

            # overlap check
            overlapping = has_overlap(staff.userId, start_dt, end_dt)
            if overlapping:
                print("Warning: This shift overlaps an existing shift:")
                print(f"  Existing Shift {overlapping.shiftId}: {overlapping.startTime} - {overlapping.endTime}")
                confirm = input("Proceed and still create this shift? (y/N): ").strip().lower()
                if confirm != "y":
                    print("Aborted due to overlap.")
                    return

            # create shift within transaction
            shift = Shift(rosterId=roster.rosterId, staffId=staff.userId, startTime=start_dt, endTime=end_dt)
            try:
                db.session.add(shift)
                db.session.commit()
                print(f"Scheduled shift {shift.shiftId} for staff {staff.username}: {start_dt} - {end_dt}")
            except Exception as e:
                db.session.rollback()
                print("Error saving shift to database:", str(e))
            return

        except Exception as e:
            print("Error during scheduling:", str(e))
            return

    # ------------------------------
    # INTERACTIVE MULTI-SHIFT MODE
    # ------------------------------
    print("\nInteractive scheduling mode:\n")
    print("Enter one or more shifts for staff:")
    print(f"  Staff: {staff.userId} - {staff.username} ({staff.role})")
    print("Date/time format examples:")
    print("  Start/End : 2025-09-29T09:00  (YYYY-MM-DDTHH:MM)")
    print("  Week-start : 2025-09-29       (YYYY-MM-DD)  - optional\n")

    # Optionally get week-start first (applies only if you want a single roster for all shifts)
    fixed_week = None
    if week_start:
        try:
            fixed_week = parse_date(week_start)
        except Exception:
            print("Warning: invalid --week-start format ignored; continuing without fixed week.")

    shifts_to_create = []
    while True:
        raw_start = input("Enter shift START datetime (or 'done' to finish): ").strip()
        if raw_start.lower() == "done":
            break
        # parse start
        try:
            start_dt = parse_dt(raw_start)
        except Exception:
            print("Invalid start format. Use YYYY-MM-DDTHH:MM (e.g. 2025-09-29T09:00).")
            continue

        raw_end = input("Enter shift END datetime: ").strip()
        try:
            end_dt = parse_dt(raw_end)
        except Exception:
            print("Invalid end format. Use YYYY-MM-DDTHH:MM (e.g. 2025-09-29T17:00).")
            continue

        if start_dt >= end_dt:
            print("Error: start must be before end. Try again.")
            continue

        # If user gave a fixed week, use it; otherwise compute roster week for this shift
        if fixed_week:
            ws = fixed_week
        else:
            ws = start_dt.date() - timedelta(days=start_dt.weekday())

        # Check overlap
        overlapping = has_overlap(staff.userId, start_dt, end_dt)
        if overlapping:
            print("Warning: This shift overlaps an existing shift:")
            print(f"  Existing Shift {overlapping.shiftId}: {overlapping.startTime} - {overlapping.endTime}")
            confirm = input("Proceed and still add this shift? (y/N): ").strip().lower()
            if confirm != "y":
                print("Skipping this shift.")
                continue

        # collect this shift (create later in DB transaction)
        shifts_to_create.append((ws, start_dt, end_dt))
        print("Shift added to the batch. Add more or type 'done' to finish.\n")

    if not shifts_to_create:
        print("No shifts entered. Cancelled.")
        return

    # Summary and confirmation
    print("\nYou are about to create the following shifts:")
    for idx, (ws, st, et) in enumerate(shifts_to_create, start=1):
        print(f"  [{idx}] {st} -> {et}  (week start {ws})")
    confirm = input("Confirm create these shifts? (y/N): ").strip().lower()
    if confirm != "y":
        print("Aborted. No shifts were created.")
        return

    # Create all shifts inside a transaction
    try:
        created = []
        for ws, st, et in shifts_to_create:
            # get or create roster for that week
            roster = Roster.query.filter_by(weekStartDate=ws).first()
            if not roster:
                roster = Roster(weekStartDate=ws, weekEndDate=ws + timedelta(days=6))
                db.session.add(roster)
                db.session.flush()  # get roster.rosterId without commit

            sh = Shift(rosterId=roster.rosterId, staffId=staff.userId, startTime=st, endTime=et)
            db.session.add(sh)
            created.append(sh)

        db.session.commit()
        print(f"Created {len(created)} shifts for staff {staff.username}.")
        for sh in created:
            print(f"  - Shift {sh.shiftId}: {sh.startTime} - {sh.endTime}")

    except Exception as e:
        db.session.rollback()
        print("Error creating shifts; transaction rolled back. Error:", str(e))

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
        print(f"Shift {sh.shiftId}: {staff_name} | {sh.startTime} - {sh.endTime}")


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
    """View combined roster for the week."""
    if week_start:
        ws = parse_date(week_start)
        roster = Roster.query.filter_by(weekStartDate=ws).first()
        if not roster:
            print("No roster found for that week.")
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
    print(f"Staff {staff_id} timed in for shift {shift_id} at {ts}")


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
    print(f"Staff {staff_id} timed out for shift {shift_id} at {ts}")


# ---------- Register CLI groups ----------
app.cli.add_command(system_cli)
app.cli.add_command(admin_cli)
app.cli.add_command(staff_cli)
