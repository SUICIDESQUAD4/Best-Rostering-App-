# Best Rostering App (CLI)

A command-line rostering application built with Flask, SQLAlchemy, and Click.  
Admins can schedule staff shifts, track attendance, and generate weekly shift reports.  
Designed for simplicity, database best practices, and beginner-friendly usage.

---

## Dependencies

* Python3 / pip3
* Packages listed in `requirements.txt`

---

## Installing Dependencies

```bash
$ pip install -r requirements.txt
```

---

## Configuration Management

Configuration such as database URL/port, credentials, and secrets should not be committed to public repositories.

Provide configuration via a `default_config.py` file for development or environment variables in production.

### In Development

By default, the app uses a SQLite database stored locally:

`default_config.py`
```python
SQLALCHEMY_DATABASE_URI = "sqlite:///temp-database.db"
SECRET_KEY = "secret key"
ENV = "DEVELOPMENT"
```

These values are loaded inside `config.py`.

### In Production

Pass configuration through environment variables on your hosting platform (e.g., Render, Heroku).

---

## Flask Commands

The project uses `wsgi.py` as a utility script for CLI commands.

Commands are grouped into three categories:
* `system` – Database setup and maintenance
* `admin` – Manage staff and schedule shifts
* `staff` – Staff functions like viewing rosters and recording attendance

---

## Running the Project

### Development

```bash
$ flask run
```

### Production (Gunicorn)

```bash
$ gunicorn wsgi:app
```

---

## Initializing the Database

On a fresh setup, seed the database with demo data:

```bash
$ flask system init-db
```

This seeds:

* 2 Admins
* 6 Staff
* 5 Rosters (current + 4 past weeks)
* Randomized Shifts & Attendance Records

Rollback any uncommitted changes:

```bash
$ flask system rollback-db
```

---

## Database Migrations

Use Flask-Migrate if models change:

```bash
$ flask db init
$ flask db migrate
$ flask db upgrade
```

---

## CLI Usage

### System Commands

```bash
$ flask system init-db        # Initialize DB with demo data
$ flask system rollback-db    # Rollback uncommitted changes
```

### Admin Commands

```bash
$ flask admin add-staff           # Add staff interactively
$ flask admin delete-staff 2      # Delete staff by ID
$ flask admin list-staff          # List all staff
$ flask admin schedule-shift      # Interactive shift scheduling
$ flask admin list-shifts         # List all shifts
$ flask admin view-shift-report   # Select roster, generate report
```

### Staff Commands

```bash
$ flask staff view-roster --week-start 2025-09-29
$ flask staff time-in 2 5     # Staff 2 time-in for shift 5
$ flask staff time-out 2 5    # Staff 2 time-out for shift 5
```

### Example Workflow

```bash
flask system init-db
flask admin list-staff
flask admin schedule-shift
flask staff view-roster --week-start 2025-09-29
flask staff time-in 2 5
flask staff time-out 2 5
flask admin view-shift-report
```

---

## Testing

Currently, the app supports manual testing via CLI commands.

Automated tests can be added under `App/test`.

To run all tests:

```bash
$ pytest
```

For coverage:

```bash
$ coverage report
$ coverage html
```

---

## Troubleshooting

### Staff not found

Add staff first:

```bash
flask admin add-staff
```

### No roster found

Schedule shifts:

```bash
flask admin schedule-shift
```

### Database errors

Rollback or reset DB:

```bash
flask system rollback-db
flask system init-db
```
