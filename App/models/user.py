from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from App.models.roster import Roster

class User(db.Model):
    __tablename__ = "users"
    userId = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    passwordHash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": type
    }

    def viewRoster(self, week_start=None):
        """Return roster view — proxy to Roster.getCombinedRoster for a week if needed."""
        
        if week_start:
            roster = Roster.get_or_create_by_week(week_start)
            return roster.getCombinedRoster()
        return "Use view-roster command to see roster."

    # def __init__(self, username, password):
    #     self.username = username
    #     self.set_password(password)

    # def get_json(self):
    #     return{
    #         'id': self.id,
    #         'username': self.username
    #     }

    # def set_password(self, password):
    #     """Create hashed password."""
    #     self.password = generate_password_hash(password)
    
    # def check_password(self, password):
    #     """Check hashed password."""
    #     return check_password_hash(self.password, password)

