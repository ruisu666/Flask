from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.forms import LoginForm 
from app.utils import execute_query

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

        query = "SELECT * FROM tbladmin WHERE username = %s AND password = %s"
        result = execute_query(query, (username, password), fetchone=True)

        if result:
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')
