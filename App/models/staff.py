from App.database import db
from App.models.user import User

class Staff(User):
    __tablename__ = "staff"
    userId = db.Column(db.Integer, db.ForeignKey("users.userId"), primary_key=True)
    role = db.Column(db.String(50))

    __mapper_args__ = {
        "polymorphic_identity": "staff"
    }

    def timeIn(self, shift):
        return f"{self.username} clocked in at {shift.startTime}"

    def timeOut(self, shift):
        return f"{self.username} clocked out at {shift.endTime}"
