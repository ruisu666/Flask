from flask import Blueprint, render_template, flash, redirect, url_for, session, request
from app.forms import LoginForm 
from app.utils import (
    get_cursor,
    get_db_connection,
    close_db_connection,
    logout_user
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.adminlogin'))

@auth_bp.route('/login/admin', methods=['GET', 'POST'])
def adminlogin():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        try:
            cursor, connection = get_cursor()
        except AttributeError:
            flash('Error connecting to the database. Please try again later.', 'danger')
            return redirect(url_for('auth.adminlogin'))
        
        if connection is not None:
            query = "SELECT adminID, username, password FROM admin WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            if user:
                admin_id, username, password = user
                session['adminID'] = admin_id
                flash('Login successful!', 'success')
                cursor.close()
                close_db_connection(connection)
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash('Login unsuccessful. Please check username and password', 'danger')
                cursor.close()
                close_db_connection(connection)

        else:
            flash('Error connecting to the database. Please try again later.', 'danger')
            return redirect(url_for('auth.adminlogin'))
    
    return render_template('adminlogin.html', title='Log In', form=form)

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear() 
        print("Session Check in Logout Route: ", session)
        return redirect(url_for('auth.adminlogin'))  
    else:
        return render_template("adminlogin.html")

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')
