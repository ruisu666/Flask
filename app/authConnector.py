from flask import Blueprint, render_template, flash, redirect, url_for, session
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
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        cursor, connection = get_cursor()
        if connection is not None:
            query = "SELECT * FROM tbladmin WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            if user:
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash('Login unsuccessful. Please check username and password', 'danger')

            cursor.close()
            close_db_connection()
        else:
            flash('Error connecting to the database. Please try again later.', 'danger')
    
    return render_template('login.html', title='Log In', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')
