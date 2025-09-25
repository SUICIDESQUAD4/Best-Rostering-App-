from App.database import db

class Shift(db.Model):
    __tablename__ = "shifts"
    shiftId = db.Column(db.Integer, primary_key=True)
    startTime = db.Column(db.DateTime, nullable=False)
    endTime = db.Column(db.DateTime, nullable=False)
    staffId = db.Column(db.Integer, db.ForeignKey("staff.userId"))

    def assignStaff(self, staff):
        self.staffId = staff.userId
        return f"Assigned {staff.username} to shift {self.shiftId}"

    def getDuration(self):
        return (self.endTime - self.startTime).seconds // 3600
