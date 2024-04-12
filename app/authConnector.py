from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_mail import Mail
from app.forms import LoginForm, RegistrationForm
from app.utils import get_cursor, close_db_connection, logout_user, log_in_user, send_verification_email, generate_verification_token, verify_token
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from app.dashboardConnector import dashboard_bp
from app import app
from flask import request
import requests
import base64
import qrcode
import io

auth_bp = Blueprint('auth', __name__)
mail = Mail(app) 

@auth_bp.route('/')
def landing():
    return render_template('landing.html')

@auth_bp.route('/login/user', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        # Verify reCAPTCHA
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not recaptcha_response:
            flash('Please complete the reCAPTCHA challenge.', 'danger')
            return redirect(url_for('auth.user_login'))
        
        recaptcha_secret_key = '6LfP-rUpAAAAAMfSpH2D0HIKxOodLKtgEi8Qxzdu'  
        verification_url = 'https://www.google.com/recaptcha/api/siteverify'
        params = {
            'secret': recaptcha_secret_key,
            'response': recaptcha_response
        }
        response = requests.post(verification_url, data=params)
        if not response.json().get('success'):
            flash('reCAPTCHA verification failed. Please try again.', 'danger')
            return redirect(url_for('auth.user_login'))

        email = form.email.data
        password = form.password.data

        print("Email entered:", email)  # Debugging print
        print("Password entered:", password)  # Debugging print

        try:
            cursor, connection = get_cursor()
        except AttributeError:
            flash('Error connecting to the database. Please try again later.', 'danger')
            return redirect(url_for('auth.user_login'))

        if connection is not None:
            query = "SELECT infoID, firstname, password FROM userinfo WHERE email = %s"
            print("Query:", query)  # Debugging print
            cursor.execute(query, (email,))
            user_info = cursor.fetchone()

            print("Session before login:", session)  # Debugging print

            if user_info and check_password_hash(user_info[2], password):
                info_id = user_info[0]
                user_firstname = user_info[1]  # Fetching user's first name
                session['infoID'] = info_id
                session['user_role'] = 'user'
                session['user_firstname'] = user_firstname  # Storing user's first name in the session
                log_in_user(email, info_id, 'user')
                flash('User login successful!', 'success')
                cursor.close()
                close_db_connection(connection)
                print("User login successful!") # Debugging print
                return redirect(url_for('dashboard.dashboard'))
            elif user_info:
                flash('Invalid email or password', 'danger')
            else:
                flash('Email is not registered', 'danger')
                cursor.close()
                close_db_connection(connection)
                print("Email is not registered") # Debugging print
                return redirect(url_for('auth.user_login'))
        else:
            flash('Error connecting to the database. Please try again later.', 'danger')
            return redirect(url_for('auth.user_login'))
    
    print("Form validation failed") # Debugging print
    return render_template('user_login.html', title='User Log In', form=form)

@auth_bp.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()

    if form.validate_on_submit():
        # Verify reCAPTCHA
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not recaptcha_response:
            flash('Please complete the reCAPTCHA challenge.', 'danger')
            return redirect(url_for('auth.admin_login'))
        
        recaptcha_secret_key = '6LfP-rUpAAAAAMfSpH2D0HIKxOodLKtgEi8Qxzdu'  
        verification_url = 'https://www.google.com/recaptcha/api/siteverify'
        params = {
            'secret': recaptcha_secret_key,
            'response': recaptcha_response
        }
        response = requests.post(verification_url, data=params)
        if not response.json().get('success'):
            flash('reCAPTCHA verification failed. Please try again.', 'danger')
            return redirect(url_for('auth.admin_login'))

        email = form.email.data
        password = form.password.data

        print("Email entered:", email)  
        print("Password entered:", password)  

        try:
            cursor, connection = get_cursor()
        except AttributeError:
            flash('Error connecting to the database. Please try again later.', 'danger')
            return redirect(url_for('auth.admin_login'))

        if connection is not None:
            query = "SELECT adminID, password FROM admin WHERE email = %s"
            print("Query:", query)  
            cursor.execute(query, (email,))
            admin_info = cursor.fetchone()

            print("Session before login:", session) 

            if admin_info and check_password_hash(admin_info[1], password):
                admin_id = admin_info[0]
                session['adminID'] = admin_id
                session['user_role'] = 'admin'
                log_in_user(email, admin_id, 'admin') 
                flash('Admin login successful!', 'success')
                cursor.close()
                close_db_connection(connection)
                print("Admin login successful!") # Debugging print
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash('Invalid email or password', 'danger')

        else:
            flash('Error connecting to the database. Please try again later.', 'danger')

    return render_template('admin_login.html', title='Admin Log In', form=form)

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.landing'))

@auth_bp.route('/register/user', methods=['GET', 'POST'])
def register_user():
    form = RegistrationForm()

    if form.validate_on_submit():
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not recaptcha_response:
            flash('Please complete the reCAPTCHA challenge.', 'danger')
            return redirect(url_for('auth.register_user'))

        recaptcha_secret_key = '6LfP-rUpAAAAAMfSpH2D0HIKxOodLKtgEi8Qxzdu'  
        verification_url = 'https://www.google.com/recaptcha/api/siteverify'
        params = {
            'secret': recaptcha_secret_key,
            'response': recaptcha_response
        }
        response = requests.post(verification_url, data=params)
        if not response.json().get('success'):
            flash('reCAPTCHA verification failed. Please try again.', 'danger')
            return redirect(url_for('auth.register_user'))

        password_hash = generate_password_hash(form.password.data) 

        session['registration_data'] = {
            'studno': form.studno.data,
            'firstname': form.firstname.data,
            'lastname': form.lastname.data,
            'email': form.emailaddress.data,
            'contactnumber': form.contactnumber.data,
            'password': password_hash,  
            'licenseplate': form.license_number.data,
            'model': form.vehicle_model.data
        }

        token = generate_verification_token()

        session['verification_token'] = token

        send_verification_email(form.emailaddress.data, token)


        print("Student Number:", form.studno.data)
        print("First Name:", form.firstname.data)
        print("Last Name:", form.lastname.data)
        print("Email Address:", form.emailaddress.data)
        print("Contact Number:", form.contactnumber.data)
        print("Password:", form.password.data)
        print("License Plate Number:", form.license_number.data)
        print("Vehicle Model:", form.vehicle_model.data)
        flash_message = 'A verification email has been sent to your email address. Please verify your email to complete registration.'
        flash_link = url_for('auth.resend_verification_email')
        flash(flash_message, 'verification_success_message')
        flash(flash_link, 'flash_link')

        return redirect(url_for('auth.user_login'))

    return render_template('register_user.html', form=form)

@auth_bp.route('/resend_verification_email', methods=['GET'])
def resend_verification_email():
    email_address = session.get('registration_data', {}).get('email')

    if email_address:
        token = generate_verification_token()

        session['verification_token'] = token

        send_verification_email(email_address, token)

        flash('A verification email has been resent to your email address.', 'success')
        return redirect(url_for('auth.login'))

    else:
        flash('No email address found in the registration data. Please try registering again.', 'danger')

    return redirect(url_for('auth.register_user'))

@auth_bp.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    if verify_token(token):
        registration_data = session.get('registration_data')

        if registration_data:
            try:
                cursor, connection = get_cursor()

                password_hash = registration_data['password']

                sql_userinfo = "INSERT INTO userinfo (studno, lastname, firstname, email, contactnumber, password) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql_userinfo, (
                    registration_data['studno'],
                    registration_data['lastname'],
                    registration_data['firstname'],
                    registration_data['email'],
                    registration_data['contactnumber'],
                    password_hash  
                ))
                connection.commit()

                user_id = cursor.lastrowid

                sql_vehicle = "INSERT INTO vehicle (userID, licenseplate, model) VALUES (%s, %s, %s)"
                cursor.execute(sql_vehicle, (user_id, registration_data['licenseplate'], registration_data['model']))
                connection.commit()

                qr_data = f"Studno: {registration_data['studno']}\nLastname: {registration_data['lastname']}\nFirstname: {registration_data['firstname']}\nEmail: {registration_data['email']}\nContact Number: {registration_data['contactnumber']}\nLicense Plate: {registration_data['licenseplate']}\nVehicle Model: {registration_data['model']}"

                qr_image_str = generate_qr_code(qr_data)

                sql_qr_code = "INSERT INTO qr_codes (userID, qr_code_image) VALUES (%s, %s)"
                cursor.execute(sql_qr_code, (user_id, qr_image_str))
                connection.commit()

                flash('Your email has been verified. You can now log in.', 'success')
                cursor.close()
                close_db_connection(connection)
                session.pop('registration_data')
                return redirect(url_for('auth.user_login'))
            except mysql.connector.Error as err:
                flash('Error registering user or vehicle: {}'.format(err), 'danger')
                cursor.close()
                close_db_connection(connection)
                return redirect(url_for('auth.user_login'))
        else:
            flash('Registration data not found. Please try registering again.', 'danger')
            return redirect(url_for('auth.user_login'))
    else:
        flash('Invalid or expired verification token.', 'danger')
        return redirect(url_for('auth.user_login'))

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create a PIL Image object
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert the PIL Image to a bytes object
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Encode the bytes object as a Base64 string
    img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
    
    return img_base64








