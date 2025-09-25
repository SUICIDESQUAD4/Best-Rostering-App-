from App.database import db
from App.models.user import User

class Admin(User):
    __tablename__ = "admins"
    userId = db.Column(db.Integer, db.ForeignKey("users.userId"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }

    def scheduleShift(self, staff, shift):
        return f"Scheduled {staff.username} for shift {shift.shiftId}"

    def viewShiftReport(self, report):
        return f"Viewing report: {report.reportId}"

    def addStaff(self, staff):
        return f"Staff {staff.username} added"

    def deleteStaff(self, staff):
        return f"Staff {staff.username} deleted"
