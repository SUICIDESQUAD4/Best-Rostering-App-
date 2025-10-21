# App/views/index.py

from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, current_user

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/')
def index_page():
    return render_template('index.html')

@index_views.route('/admin/dashboard')
@jwt_required(optional=True)
def admin_dashboard():
    if not current_user or current_user.type != "admin":
        return redirect(url_for('index_views.index_page'))
    return render_template('admin_dashboard.html', user=current_user)

@index_views.route('/staff/dashboard')
@jwt_required(optional=True)
def staff_dashboard():
    if not current_user or current_user.type != "staff":
        return redirect(url_for('index_views.index_page'))
    return render_template('staff_dashboard.html', user=current_user)

