from App.database import db

class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"
    recordId = db.Column(db.Integer, primary_key=True)
    staffId = db.Column(db.Integer, db.ForeignKey("staff.userId"))
    shiftId = db.Column(db.Integer, db.ForeignKey("shifts.shiftId"))
    timeIn = db.Column(db.DateTime)
    timeOut = db.Column(db.DateTime)

    def markTimeIn(self, staff, shift):
        self.staffId = staff.userId
        self.shiftId = shift.shiftId
        return f"{staff.username} clocked in for shift {shift.shiftId}"

    def markTimeOut(self, staff, shift):
        return f"{staff.username} clocked out of shift {shift.shiftId}"
