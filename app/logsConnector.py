from flask import render_template, redirect, url_for, flash, request, session, Blueprint

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/logs', methods=['GET'])
def logs():
    user_role = session.get('user_role')

    if user_role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('logs.html', title='Logs', user_role=user_role)
