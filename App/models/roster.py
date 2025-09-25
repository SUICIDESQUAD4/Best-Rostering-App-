from App.database import db

class Roster(db.Model):
    __tablename__ = "rosters"
    rosterId = db.Column(db.Integer, primary_key=True)

    def getCombinedRoster(self):
        return f"Combined roster for roster {self.rosterId}"
