# App/models/user.py
from typing import Optional
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Mapped, mapped_column

from App.database import db

class User(db.Model):
    __tablename__ = "users"
    # Use mapped_column (SQLA 2 style), but db types remain available
    userId: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    passwordHash: Mapped[str] = mapped_column(db.String(256), nullable=False)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    type: Mapped[Optional[str]] = mapped_column(db.String(50), nullable=True)

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "user"
    }

    def set_password(self, raw_password: str):
        """Hash and set the user's password."""
        self.passwordHash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verify hashed password."""
        if not self.passwordHash:
            return False
        return check_password_hash(self.passwordHash, raw_password)
    def get_json(self):
        """Return a dictionary representation of the user."""
        return {
            "userId": self.userId,
            "username": self.username,
            "email": self.email,
            "type": self.type
        }

