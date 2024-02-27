from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        print("Form submitted")
        print("Email:", form.email.data)
        print("Password:", form.password.data)

        hardcoded_email = 'sangoku'
        hardcoded_password = '123'

        if form.email.data == hardcoded_email and form.password.data == hardcoded_password:
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', form=form)

@auth_bp.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    return render_template('register.html', form=form)
