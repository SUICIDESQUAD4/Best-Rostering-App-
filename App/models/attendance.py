from App.database import db

class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"
    recordId = db.Column(db.Integer, primary_key=True)
    staffId = db.Column(db.Integer, db.ForeignKey("staff.userId"), nullable=False)
    shiftId = db.Column(db.Integer, db.ForeignKey("shifts.shiftId"), nullable=False)
    timeIn = db.Column(db.DateTime, nullable=True)
    timeOut = db.Column(db.DateTime, nullable=True)

    @classmethod
    def get_or_create(cls, staff_id, shift_id):
        rec = cls.query.filter_by(staffId=staff_id, shiftId=shift_id).first()
        if not rec:
            rec = cls(staffId=staff_id, shiftId=shift_id)
            db.session.add(rec)
            db.session.commit()
        return rec

    def markTimeIn(self, ts):
        self.timeIn = ts
        db.session.add(self)
        db.session.commit()

    def markTimeOut(self, ts):
        self.timeOut = ts
        db.session.add(self)
        db.session.commit()

