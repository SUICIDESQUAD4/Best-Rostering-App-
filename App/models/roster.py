from App.database import db

class Roster(db.Model):
    __tablename__ = "rosters"
    rosterId = db.Column(db.Integer, primary_key=True)
    weekStartDate = db.Column(db.Date, nullable=False)
    weekEndDate = db.Column(db.Date, nullable=False)

    def getCombinedRoster(self):
        from App.models.shift import Shift
        return Shift.query.filter_by(rosterId=self.rosterId).all()
    
    def get_json(self):
        return {
            "rosterId": self.rosterId,
            "weekStartDate": self.weekStartDate.isoformat(),
            "weekEndDate": self.weekEndDate.isoformat(),
            "shifts": [shift.get_json() for shift in self.getCombinedRoster()]
        }
