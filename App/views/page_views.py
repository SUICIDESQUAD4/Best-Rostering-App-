from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.database import db
from App.models.user import User

page_bp = Blueprint('pages', __name__)

from flask import render_template

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/admin/dashboard')
def admin_dashboard_page():
    return render_template('admin_dashboard.html')

@app.route('/staff/dashboard')
def staff_dashboard_page():
    return render_template('staff_dashboard.html')


@page_bp.route("/")
def index():
    return render_template("index.html")

@page_bp.route("/admin/dashboard")
@jwt_required(optional=True)
def admin_dashboard():
    user_id = get_jwt_identity()
    if not user_id:
        return redirect(url_for('pages.index'))

    user = db.session.get(User, int(user_id))
    if not user or user.type != "admin":
        return redirect(url_for('pages.index'))

    return render_template("admin_dashboard.html", user=user)

@page_bp.route("/staff/dashboard")
@jwt_required(optional=True)
def staff_dashboard():
    user_id = get_jwt_identity()
    if not user_id:
        return redirect(url_for('pages.index'))

    user = db.session.get(User, int(user_id))
    if not user or user.type != "staff":
        return redirect(url_for('pages.index'))

    return render_template("staff_dashboard.html", user=user)
