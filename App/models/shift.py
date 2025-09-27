from App.database import db
from datetime import datetime

class Shift(db.Model):
    __tablename__ = "shifts"
    shiftId = db.Column(db.Integer, primary_key=True)
    rosterId = db.Column(db.Integer, db.ForeignKey("rosters.rosterId"), nullable=False)
    staffId = db.Column(db.Integer, db.ForeignKey("staff.userId"), nullable=True)
    startTime = db.Column(db.DateTime, nullable=False)
    endTime = db.Column(db.DateTime, nullable=False)

    def assignStaff(self, staff):
        self.staffId = staff.userId
        db.session.add(self)
        db.session.commit()

    def getDurationHours(self):
        return (self.endTime - self.startTime).total_seconds() / 3600.0
