from App.database import db

class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"
    recordId = db.Column(db.Integer, primary_key=True)
    staffId = db.Column(db.Integer, db.ForeignKey("staff.userId"))
    shiftId = db.Column(db.Integer, db.ForeignKey("shifts.shiftId"))
    timeIn = db.Column(db.DateTime)
    timeOut = db.Column(db.DateTime)

    @staticmethod
    def get_or_create(staff_id, shift_id):
        record = AttendanceRecord.query.filter_by(staffId=staff_id, shiftId=shift_id).first()
        if not record:
            record = AttendanceRecord(staffId=staff_id, shiftId=shift_id)
            db.session.add(record)
            db.session.commit()
        return record

    def markTimeIn(self, ts):
        self.timeIn = ts
        db.session.commit()

    def markTimeOut(self, ts):
        self.timeOut = ts
        db.session.commit()
