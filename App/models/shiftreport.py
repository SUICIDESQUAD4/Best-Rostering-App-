from App.database import db

class ShiftReport(db.Model):
    __tablename__ = "shift_reports"
    reportId = db.Column(db.Integer, primary_key=True)
    weekStartDate = db.Column(db.Date, nullable=False)
    weekEndDate = db.Column(db.Date, nullable=False)
    summary = db.Column(db.String(500))

    def generateReport(self, roster, attendance):
        return f"Generated report for {self.weekStartDate} to {self.weekEndDate}"
