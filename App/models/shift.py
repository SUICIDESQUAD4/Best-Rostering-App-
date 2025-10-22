from App.database import db

class Shift(db.Model):
    __tablename__ = "shifts"
    shiftId = db.Column(db.Integer, primary_key=True)
    rosterId = db.Column(db.Integer, db.ForeignKey("rosters.rosterId"))
    staffId = db.Column(db.Integer, db.ForeignKey("staff.userId"))
    startTime = db.Column(db.DateTime, nullable=False)
    endTime = db.Column(db.DateTime, nullable=False)

    def assignStaff(self, staff):
        self.staffId = staff.userId
        return f"Assigned {staff.username} to shift {self.shiftId}"

    def getDuration(self):
        return (self.endTime - self.startTime).seconds // 3600

    def get_json(self):
        return {
            "shiftId": self.shiftId,
            "rosterId": self.rosterId,
            "staffId": self.staffId,
            "startTime": self.startTime.isoformat() if self.startTime else None,
            "endTime": self.endTime.isoformat() if self.endTime else None
        }