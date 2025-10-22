from App.database import db

class ShiftReport(db.Model):
    __tablename__ = "shift_reports"
    reportId = db.Column(db.Integer, primary_key=True)
    rosterId = db.Column(db.Integer, db.ForeignKey("rosters.rosterId"))
    weekStartDate = db.Column(db.Date, nullable=False)
    weekEndDate = db.Column(db.Date, nullable=False)
    summary = db.Column(db.String(5000))

    def generateReport(self, roster, attendance):
        staff_count = len({a.staffId for a in attendance})
        shift_count = len({a.shiftId for a in attendance})
        self.summary = f"Report covers {staff_count} staff and {shift_count} shifts."
        db.session.commit()
        return self.summary
