from App.database import db
from datetime import datetime, timedelta, date

class Roster(db.Model):
    __tablename__ = "rosters"
    rosterId = db.Column(db.Integer, primary_key=True)
    weekStartDate = db.Column(db.Date, nullable=False)
    weekEndDate = db.Column(db.Date, nullable=False)

    # composition relation handled by Shift.rosterId

    @staticmethod
    def week_bounds(week_start_date):
        ws = week_start_date
        we = ws + timedelta(days=6)
        return ws, we

    @classmethod
    def get_or_create_by_week(cls, week_start):
        if isinstance(week_start, str):
            week_start = date.fromisoformat(week_start)
        ws, we = cls.week_bounds(week_start)
        roster = cls.query.filter_by(weekStartDate=ws).first()
        if not roster:
            roster = cls(weekStartDate=ws, weekEndDate=we)
            db.session.add(roster)
            db.session.commit()
        return roster

    def getCombinedRoster(self):
        from App.models.shift import Shift
        shifts = Shift.query.filter_by(rosterId=self.rosterId).order_by(Shift.startTime).all()
        return shifts
