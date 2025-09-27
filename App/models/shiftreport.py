from App.database import db

class ShiftReport(db.Model):
    __tablename__ = "shift_reports"
    reportId = db.Column(db.Integer, primary_key=True)
    rosterId = db.Column(db.Integer, db.ForeignKey("rosters.rosterId"), nullable=False)
    weekStartDate = db.Column(db.Date, nullable=False)
    weekEndDate = db.Column(db.Date, nullable=False)
    summary = db.Column(db.String(2000), nullable=True)

    def generateReport(self, roster, attendance_records):
        # Build simple summary: hours per staff and missing punches
        from collections import defaultdict
        staff_hours = defaultdict(float)
        missing = []
        for rec in attendance_records:
            # assume shift relation loaded
            if rec.timeIn and rec.timeOut:
                dur = (rec.timeOut - rec.timeIn).total_seconds() / 3600.0
                staff_hours[rec.staffId] += dur
            else:
                missing.append(rec)
        lines = [f"Report for {self.weekStartDate} to {self.weekEndDate}"]
        for sid, hours in staff_hours.items():
            lines.append(f"Staff {sid}: {hours:.2f} hours")
        lines.append(f"Missing or incomplete punches: {len(missing)}")
        self.summary = "\n".join(lines)
        db.session.add(self)
        db.session.commit()
        return self.summary

