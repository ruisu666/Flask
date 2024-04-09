from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_mail import Mail
from app.forms import LoginForm, RegistrationForm
from app.utils import get_cursor, close_db_connection, logout_user, log_in_user, send_verification_email, generate_verification_token, verify_token
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from app.dashboardConnector import dashboard_bp
from app import app

auth_bp = Blueprint('auth', __name__)
mail = Mail(app)  # Initialize Mail with the Flask app instance

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        try:
            cursor, connection = get_cursor()
        except AttributeError:
            flash('Error connecting to the database. Please try again later.', 'danger')
            return redirect(url_for('auth.login'))

        if connection is not None:
            # Check if the email exists in the admin table
            query = "SELECT adminID, password FROM admin WHERE email = %s"
            cursor.execute(query, (email,))
            admin_info = cursor.fetchone()

            if admin_info and check_password_hash(admin_info[1], password):
                admin_id = admin_info[0]
                session['adminID'] = admin_id
                session['user_role'] = 'admin'
                log_in_user(email, admin_id, 'admin')  # Log in the user
                flash('Admin login successful!', 'success')
                cursor.close()
                close_db_connection(connection)
                return redirect(url_for('dashboard.dashboard'))

            # Check if the email exists in the userinfo table
            query = "SELECT infoID, password FROM userinfo WHERE email = %s"
            cursor.execute(query, (email,))
            user_info = cursor.fetchone()

            if user_info and check_password_hash(user_info[1], password):
                info_id = user_info[0]
                session['infoID'] = info_id
                session['user_role'] = 'user'
                log_in_user(email, info_id, 'user')  # Log in the user
                flash('User login successful!', 'success')
                cursor.close()
                close_db_connection(connection)
                return redirect(url_for('dashboard.dashboard'))

            flash('Invalid email or password', 'danger')
            cursor.close()
            close_db_connection(connection)
        else:
            flash('Error connecting to the database. Please try again later.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html', title='Log In', form=form)

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        password_hash = generate_password_hash(form.password.data)  # Hash the password

        session['registration_data'] = {
            'studno': form.studno.data,
            'firstname': form.firstname.data,
            'lastname': form.lastname.data,
            'email': form.emailaddress.data,
            'contactnumber': form.contactnumber.data,
            'password': password_hash,  # Store the hashed password
            'licenseplate': form.license_number.data,
            'model': form.vehicle_model.data
        }

        token = generate_verification_token()

        # Store the token in the session
        session['verification_token'] = token

        # Send verification email
        send_verification_email(form.emailaddress.data, token)

        flash_message = 'A verification email has been sent to your email address. Please verify your email to complete registration.'
        flash_link = url_for('auth.resend_verification_email')
        flash(flash_message, 'success')
        flash(flash_link, 'flash_link')

        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth_bp.route('/resend_verification_email', methods=['GET'])
def resend_verification_email():
    # Get the email address from the registration data in the session
    email_address = session.get('registration_data', {}).get('email')

    if email_address:
        # Generate a new verification token
        token = generate_verification_token()

        # Store the token in the session
        session['verification_token'] = token

        # Send verification email
        send_verification_email(email_address, token)

        flash('A verification email has been resent to your email address.', 'success')
        return redirect(url_for('auth.login'))

    else:
        flash('No email address found in the registration data. Please try registering again.', 'danger')

    return redirect(url_for('auth.register'))

@auth_bp.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    if verify_token(token):
        registration_data = session.get('registration_data')

        if registration_data:
            try:
                cursor, connection = get_cursor()

                # Hash the password
                password_hash = registration_data['password']

                # Insert user data into the userinfo table
                sql_userinfo = "INSERT INTO userinfo (studno, lastname, firstname, email, contactnumber, password) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql_userinfo, (
                    registration_data['studno'],
                    registration_data['lastname'],
                    registration_data['firstname'],
                    registration_data['email'],
                    registration_data['contactnumber'],
                    password_hash  # Store the hashed password
                ))
                connection.commit()

                # Retrieve the last inserted user ID
                user_id = cursor.lastrowid

                # Insert vehicle data into the vehicle table
                sql_vehicle = "INSERT INTO vehicle (userID, licenseplate, model) VALUES (%s, %s, %s)"
                cursor.execute(sql_vehicle, (user_id, registration_data['licenseplate'], registration_data['model']))
                connection.commit()

                flash('Your email has been verified. You can now log in.', 'success')
                cursor.close()
                close_db_connection(connection)
                session.pop('registration_data')
                return redirect(url_for('auth.login'))
            except mysql.connector.Error as err:
                flash('Error registering user or vehicle: {}'.format(err), 'danger')
                cursor.close()
                close_db_connection(connection)
                return redirect(url_for('auth.login'))
        else:
            flash('Registration data not found. Please try registering again.', 'danger')
            return redirect(url_for('auth.login'))
    else:
        flash('Invalid or expired verification token.', 'danger')
        return redirect(url_for('auth.login'))
