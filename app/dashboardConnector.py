from flask import Blueprint, render_template, flash, redirect, url_for, session
from app.utils import get_current_user_data

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    # Check user role
    user_role = session.get('user_role')
    if user_role == 'admin':
        # Render admin dashboard
        adminID = session.get('adminID')
        if not adminID:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('auth.login'))
        return render_template('dashboard.html', user_role=user_role)  # Pass user_role to the template
    elif user_role == 'user':
        # Render user dashboard
        info_id = session.get('infoID')
        if not info_id:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('auth.login'))
        return render_template('dashboard.html', user_role=user_role)  # Pass user_role to the template
    else:
        # Handle unknown user role
        flash('Please log in to access this page', 'danger')
        return redirect(url_for('auth.login'))
