# App/controllers/auth_controller.py
from typing import Optional, Dict
from flask_jwt_extended import create_access_token
from App.database import db
from App.models.user import User

def authenticate(username: str, password: str) -> Optional[Dict[str, str]]:
    """
    Authenticate a user and return an access token and role if successful.
    Returns: {"access_token": str, "role": str} or None if failed.
    """
    user = db.session.scalar(db.select(User).filter_by(username=username))
    if user and user.check_password(password):
        token = create_access_token(identity=user.userId)
        return {"access_token": token, "role": user.type}  # role will be 'staff' or 'admin'
    return None


def create_user(username: str, password: str, email: str, role: Optional[str] = None, user_type: str = "staff") -> User:
    """
    Create a new user. For staff, user_type='staff' and role can be set.
    Returns the created User object.
    """
    # Check for duplicate username
    existing = db.session.scalar(db.select(User).filter_by(username=username))
    if existing:
        raise ValueError(f"Username '{username}' already exists")

    # Create base user
    new_user = User(
        username=username,
        email=email,
        type=user_type,
        passwordHash=""
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.flush()  # Assigns PK before commit

    # If the caller is creating staff, they can attach Staff-specific info elsewhere
    db.session.commit()

    return new_user


def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Retrieve a user by their primary key ID.
    """
    return db.session.get(User, user_id)


def get_user_by_username(username: str) -> Optional[User]:
    """
    Retrieve a user by their username.
    """
    return db.session.scalar(db.select(User).filter_by(username=username))
