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

## WSGI Commands

The project uses `wsgi.py` as the main entry point and command utility.

Commands are grouped into three categories:
* `system` – Database setup and maintenance  
* `admin` – Manage staff and schedule shifts
* `staff` – Staff functions like viewing rosters and recording attendance

### Running with WSGI

Development:
```bash
$ python wsgi.py
```

Production:
```bash
$ gunicorn wsgi:app
```

---

## Database Management 

Initialize database with demo data:

```bash
$ python wsgi.py system init-db
```

This seeds:
* 2 Admins
* 6 Staff 
* 5 Rosters
* Sample shifts and attendance

Rollback changes:
```bash
$ python wsgi.py system rollback-db
```

Database migrations:
```bash
$ python wsgi.py db migrate
$ python wsgi.py db upgrade
```

---

## CLI Usage

### System Commands
```bash
$ python wsgi.py system init-db
$ python wsgi.py system rollback-db
```

### Admin Commands
```bash
$ python wsgi.py admin add-staff
$ python wsgi.py admin delete-staff 2
$ python wsgi.py admin list-staff
$ python wsgi.py admin schedule-shift
$ python wsgi.py admin list-shifts
$ python wsgi.py admin view-shift-report
```

### Staff Commands
```bash
$ python wsgi.py staff view-roster --week-start 2025-09-29
$ python wsgi.py staff time-in 2 5
$ python wsgi.py staff time-out 2 5
```

### Example Workflow
```bash
python wsgi.py system init-db
python wsgi.py admin list-staff
python wsgi.py admin schedule-shift 
python wsgi.py staff view-roster --week-start 2025-09-29
python wsgi.py staff time-in 2 5
python wsgi.py admin view-shift-report
```

---

## Testing

Run tests:
```bash
$ pytest
```

Coverage:
```bash
$ coverage run -m pytest
$ coverage report
```

---

## Troubleshooting

### Staff not found
```bash
python wsgi.py admin add-staff
```

### No roster found
```bash
python wsgi.py admin schedule-shift
```

### Database errors
```bash
python wsgi.py system rollback-db
python wsgi.py system init-db
```
