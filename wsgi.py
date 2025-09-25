import click, pytest, sys
from flask.cli import with_appcontext, AppGroup

from App.database import db, get_migrate
from App.models import User, Admin, Staff, Shift, Roster, AttendanceRecord, ShiftReport
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize )


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# --- CLI Group ---


@cli.command("init-db")
@with_appcontext
def init_db():
    db.drop_all()
    db.create_all()
    click.echo("Database initialized!")

@cli.command("create-admin")
@with_appcontext
@click.argument("username")
@click.argument("email")
@click.argument("password")
def create_admin(username, email, password):
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
    staff = Staff(username=username, email=email, password=password, role=role)
    db.session.add(staff)
    db.session.commit()
    click.echo(f"Staff {username} with role {role} created.")

@cli.command("list-staff")
@with_appcontext
def list_staff():
    staff_members = Staff.query.all()
    for s in staff_members:
        click.echo(f"{s.userId} - {s.username} ({s.role})")

# register CLI group
app.cli.add_command(cli)