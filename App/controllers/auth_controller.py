# App/controllers/auth_controller.py
from flask_jwt_extended import create_access_token
from App.database import db
from App.models.user import User

def authenticate(username: str, password: str, expected_role: str = None):
    """
    Authenticate a user by username and password.
    Optionally verify their expected role.
    Returns a JWT token if valid, otherwise None.
    """
    user = db.session.scalar(db.select(User).filter_by(username=username))

    if not user:
        return None

    if not user.check_password(password):
        return None

    if expected_role and user.type != expected_role:
        return None

    token = create_access_token(identity=user.userId)
    return token


def authenticate_user(username: str, password: str, expected_role: str):
    """
    More verbose authentication returning both token and user object.
    Useful for views.
    """
    user = db.session.scalar(db.select(User).filter_by(username=username))
    if not user or not user.check_password(password):
        return None, None
    if expected_role and user.type != expected_role:
        return None, None

    token = create_access_token(identity=user.userId)
    return token, user


def logout_user():
    """
    Stateless logout — in JWT this is usually handled on the client side
    by clearing the token. For token blacklisting, you'd add logic here.
    """
    return True
