# App/controllers/auth_controller.py
from flask_jwt_extended import create_access_token
from App.database import db
from App.models.user import User

def authenticate(username: str, password: str, role: str = None):
    """
    Authenticate a user (admin or staff) and return an access token if successful.
    Accepts optional `role` to restrict login by user type.
    Returns (token, user) if successful or None if failed.
    """
    stmt = db.select(User).filter_by(username=username)
    user = db.session.scalar(stmt)

    # Check password and (if provided) role
    if user and user.check_password(password):
        if role and user.type != role:
            # Role mismatch (e.g., staff trying to log in as admin)
            return None
        token = create_access_token(identity=user.userId)
        return token, user

    # Return single None for failed authentication (to pass tests)
    return None


def create_user(username: str, password: str, email: str, role: str = None, user_type: str = "staff") -> User:
    """
    Create a new user (staff/admin).
    """
    existing = db.session.scalar(db.select(User).filter_by(username=username))
    if existing:
        raise ValueError("Username already exists")

    new_user = User(username=username, email=email, type=user_type)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return new_user
