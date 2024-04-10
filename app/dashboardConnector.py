from flask import Blueprint, render_template, flash, redirect, url_for, session
from app.utils import get_current_user_data

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    user_role = session.get('user_role')
    if user_role == 'admin':
        adminID = session.get('adminID')
        if not adminID:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('auth.login'))
        return render_template('dashboard.html', user_role=user_role)  
    elif user_role == 'user':
        # Render user dashboard
        info_id = session.get('infoID')
        if not info_id:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('auth.login'))
        return render_template('dashboard.html', user_role=user_role) 
    else:
        flash('Please log in to access this page', 'danger')
        return redirect(url_for('auth.login'))
