from App.database import db
from datetime import datetime, date, timedelta
import random
from App.database import db

# Import models
from App.models.admin import Admin
from App.models.staff import Staff
from App.models.roster import Roster
from App.models.shift import Shift
from App.models.attendance import AttendanceRecord


def initialize():
    db.drop_all()
    db.create_all()
    # create_user('bob', 'bobpass')
    
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
