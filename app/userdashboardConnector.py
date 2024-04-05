from flask import Blueprint, render_template, flash, redirect, url_for, session

userdashboard_bp = Blueprint('dashboard', __name__)

@userdashboard_bp.route('/dashboard/user')
def dashboard():
    # Check if admin is logged in
    admin_id = session.get('adminID')
    print ("Session:", session)
    if not admin_id:
        flash('Please log in to access this page', 'danger')
        return redirect(url_for('auth.adminlogin'))

    # If admin is logged in, render dashboard template
    return render_template('userdashboard.html')

