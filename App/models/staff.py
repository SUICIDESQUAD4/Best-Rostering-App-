from App.models.user import User
from App.database import db

class Staff(User):
    __tablename__ = "staff"
    userId = db.Column(db.Integer, db.ForeignKey("users.userId"), primary_key=True)
    role = db.Column(db.String(100), nullable=True)

    __mapper_args__ = {"polymorphic_identity": "staff"}

    def __repr__(self):
        return f"<Staff {self.userId} {self.username}>"