import os, tempfile, pytest, unittest
from datetime import datetime, timedelta, date
import warnings
from sqlalchemy.exc import SAWarning
warnings.filterwarnings("ignore", category=SAWarning)


from werkzeug.security import generate_password_hash

from App.main import create_app
from App.database import db
from App.models.user import User
from App.models.admin import Admin
from App.models.staff import Staff
from App.models.roster import Roster
from App.models.shift import Shift
from App.models.attendance import AttendanceRecord
from App.controllers import auth_controller, staff_controller


"""
-------------------------------------------------------
 UNIT TESTS
-------------------------------------------------------
"""
class UserUnitTests(unittest.TestCase):

    def test_new_user_creation(self):
        user = User(username="bob", email="bob@example.com", type="staff")
        user.set_password("bobpass")
        assert user.username == "bob"
        assert user.check_password("bobpass")

    def test_password_hashing(self):
        password = "mypassword"
        user = User(username="alice", email="alice@example.com", type="staff")
        user.set_password(password)
        assert user.passwordHash != password
        assert user.check_password(password)

    def test_user_json_format(self):
        user = User(username="carol", email="carol@example.com", type="staff")
        user_json = user.get_json()
        self.assertIn("username", user_json)
        self.assertIn("type", user_json)

    def test_admin_role_inheritance(self):
        admin = Admin(username="superadmin", email="admin@example.com", type="admin")
        admin.set_password("adminpass")
        assert admin.type == "admin"
        assert admin.check_password("adminpass")

    def test_staff_role(self):
        staff = Staff(username="dave", email="dave@example.com", role="Cleaner", type="staff")
        staff.set_password("cleanpass")
        assert staff.role == "Cleaner"
        assert staff.check_password("cleanpass")


"""
-------------------------------------------------------
 INTEGRATION TESTS
-------------------------------------------------------
"""

@pytest.fixture(scope="module", autouse=True)
def app_context():
    """Creates a clean in-memory database before tests and destroys after."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


class IntegrationTests(unittest.TestCase):

    def setUp(self):
        """Create demo users and one roster for integration tests."""
        db.drop_all()
        db.create_all()

        # Admin
        self.admin = Admin(username="admin1", email="admin1@example.com", type="admin")
        self.admin.set_password("adminpass")

        # Staff
        self.staff = Staff(username="staff1", email="staff1@example.com", role="Cook", type="staff")
        self.staff.set_password("staffpass")

        db.session.add_all([self.admin, self.staff])
        db.session.commit()

        # Create roster for current week
        week_start = datetime.today() - timedelta(days=datetime.today().weekday())
        self.roster = Roster(weekStartDate=week_start.date(), weekEndDate=(week_start + timedelta(days=6)).date())
        db.session.add(self.roster)
        db.session.commit()

        # Add shift
        shift_start = datetime.now()
        shift_end = shift_start + timedelta(hours=8)
        self.shift = Shift(rosterId=self.roster.rosterId, staffId=self.staff.userId, startTime=shift_start, endTime=shift_end)
        db.session.add(self.shift)
        db.session.commit()

    def test_authenticate_valid_user(self):
        token = auth_controller.authenticate("staff1", "staffpass")
        assert token is not None

    def test_authenticate_invalid_user(self):
        token = auth_controller.authenticate("staff1", "wrongpass")
        assert token is None

    def test_roster_created(self):
        roster = Roster.query.first()
        assert roster is not None
        assert isinstance(roster.weekStartDate, date)

    def test_shift_assigned(self):
        shift = Shift.query.first()
        assert shift is not None
        assert shift.staffId == self.staff.userId

    def test_attendance_record_marking(self):
        record = AttendanceRecord.get_or_create(self.staff.userId, self.shift.shiftId)
        now = datetime.utcnow()
        record.markTimeIn(now)
        record.markTimeOut(now + timedelta(hours=8))
        db.session.commit()
        assert record.timeIn is not None
        assert record.timeOut is not None

    def test_staff_can_view_own_shifts(self):
        my_shifts = Shift.query.filter_by(staffId=self.staff.userId).all()
        assert len(my_shifts) == 1

    def test_admin_can_list_staff(self):
        staff_list = Staff.query.all()
        assert len(staff_list) >= 1

    def test_admin_can_delete_staff(self):
        staff_to_delete = Staff(username="testdel", email="del@example.com", role="Temp", type="staff")
        staff_to_delete.set_password("pass")
        db.session.add(staff_to_delete)
        db.session.commit()
        db.session.delete(staff_to_delete)
        db.session.commit()
        result = Staff.query.filter_by(username="testdel").first()
        assert result is None


if __name__ == "__main__":
    pytest.main(["-v"])
