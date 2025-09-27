from App.models.user import User
from App.database import db

class Admin(User):
    __tablename__ = "admins"
    userId = db.Column(db.Integer, db.ForeignKey("users.userId"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "admin"}