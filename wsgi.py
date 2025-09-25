import click
from flask.cli import with_appcontext, AppGroup

from App.database import db, get_migrate
from App.models import Admin, Staff, Roster, Shift 
from App.main import create_app

# Create app
app = create_app()
migrate = get_migrate(app)

# --- CLI Group ---
cli = AppGroup("rostering")

@cli.command("init")
@with_appcontext
def init_db():
    db.drop_all()
    db.create_all()

    # --- Seed Data ---
    # Create Admins
    admin1 = Admin(username="admin1", email="admin1@example.com", password="admin123")
    admin2 = Admin(username="admin2", email="admin2@example.com", password="admin456")

    # Create Staff
    staff1 = Staff(username="john_doe", email="john@example.com", password="staff123", role="Cashier")
    staff2 = Staff(username="jane_smith", email="jane@example.com", password="staff456", role="Cook")
    staff3 = Staff(username="alice_wong", email="alice@example.com", password="staff789", role="Manager")
    staff4 = Staff(username="bob_lee", email="bob@example.com", password="staff321", role="Waiter")

    # Create Rosters
    roster1 = Roster()
    roster2 = Roster()

    # Create Shifts
    from datetime import datetime, timedelta
    shift1 = Shift(startTime=datetime(2025, 9, 29, 9, 0), endTime=datetime(2025, 9, 29, 17, 0), staffId=None)
    shift2 = Shift(startTime=datetime(2025, 9, 30, 13, 0), endTime=datetime(2025, 9, 30, 21, 0), staffId=None)
    shift3 = Shift(startTime=datetime(2025, 10, 1, 8, 0), endTime=datetime(2025, 10, 1, 16, 0), staffId=None)
    shift4 = Shift(startTime=datetime(2025, 10, 2, 14, 0), endTime=datetime(2025, 10, 2, 22, 0), staffId=None)

    # Add to session
    db.session.add_all([admin1, admin2, staff1, staff2, staff3, staff4, roster1, roster2, shift1, shift2, shift3, shift4])

    db.session.commit()

    click.echo("Database initialized with sample data!")
    click.echo("Created: 2 Admins, 4 Staff, 2 Rosters, 4 Shifts")

@cli.command("create-admin")
@with_appcontext
@click.argument("username")
@click.argument("email")
@click.argument("password")
def create_admin(username, email, password):
    """Create an admin user."""
    admin = Admin(username=username, email=email, password=password)
    db.session.add(admin)
    db.session.commit()
    click.echo(f"Admin {username} created.")

@cli.command("create-staff")
@with_appcontext
@click.argument("username")
@click.argument("email")
@click.argument("password")
@click.argument("role")
def create_staff(username, email, password, role):
    """Create a staff user with a role."""
    staff = Staff(username=username, email=email, password=password, role=role)
    db.session.add(staff)
    db.session.commit()
    click.echo(f"Staff {username} with role {role} created.")

@cli.command("list-staff")
@with_appcontext
def list_staff():
    """List all staff members."""
    staff_members = Staff.query.all()
    for s in staff_members:
        click.echo(f"{s.id} - {s.username} ({s.role})")

# Register CLI group with Flask app
app.cli.add_command(cli)
