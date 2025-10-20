# App/models/staff.py
from sqlalchemy.orm import mapped_column, Mapped
from App.database import db
from App.models.user import User

class Staff(User):
    __tablename__ = "staff"
    userId: Mapped[int] = mapped_column(db.Integer, db.ForeignKey("users.userId"), primary_key=True)
    role: Mapped[str] = mapped_column(db.String(50), nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "staff"
    }

    def to_dict(self):
        d = super().to_dict()
        d.update({"role": self.role})
        return d
