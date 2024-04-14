from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_mail import Mail
from app.forms import LoginForm, UserRegistrationForm,AdminRegistrationForm
from app.utils import get_cursor, close_db_connection, logout_user, log_in_user, send_user_verification_email, generate_verification_token, verify_token,send_admin_verification_email
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

        print("Email entered:", email)  
        print("Password entered:", password)  

        try:
            cursor, connection = get_cursor()
        except AttributeError as e:
            print("Error connecting to the database:", e)
            flash('Error connecting to the database. Please try again later.', 'danger')
            return redirect(url_for('auth.user_login'))

        if connection is not None:
            query = "SELECT infoID, firstname, password FROM userinfo WHERE email = %s"
            print("Query:", query)  
            cursor.execute(query, (email,))
            user_info = cursor.fetchone()

            print("Session before login:", session)  

            if user_info:
                stored_password_hash = user_info[2]
                if check_password_hash(stored_password_hash, password):
                    info_id = user_info[0]
                    user_firstname = user_info[1]  
                    session['infoID'] = info_id
                    session['user_role'] = 'user'
                    session['user_firstname'] = user_firstname  
                    log_in_user(email, info_id, 'user')
                    flash('User login successful!', 'success')
                    cursor.close()
                    close_db_connection(connection)
                    print("User login successful!") 
                    return redirect(url_for('dashboard.dashboard'))
                else:
                    print("Invalid password for email:", email) 
                    flash('Invalid email or password', 'danger')
            else:
                print("Email is not registered:", email)  
                flash('Email is not registered', 'danger')

            cursor.close()
            close_db_connection(connection)
        else:
            flash('Error connecting to the database. Please try again later.', 'danger')

    else:
        print("Form validation failed:", form.errors) 

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
        except AttributeError as e:
            print("Error connecting to the database:", e)  
            flash('Error connecting to the database. Please try again later.', 'danger')
            return redirect(url_for('auth.admin_login'))

        if connection is not None:
            query = "SELECT adminID, password, firstname FROM admin WHERE email = %s"
            print("Query:", query)  
            cursor.execute(query, (email,))
            admin_info = cursor.fetchone()

            print("Session before login:", session) 

            if admin_info:
                stored_password_hash = admin_info[1]
                if check_password_hash(stored_password_hash, password):
                    admin_id = admin_info[0]
                    admin_firstname = admin_info[2]
                    session['adminID'] = admin_id
                    session['user_role'] = 'admin'
                    session['admin_firstname'] = admin_firstname
                    log_in_user(email, admin_id, 'admin') 
                    flash('Admin login successful!', 'success')
                    cursor.close()
                    close_db_connection(connection)
                    print("Admin login successful!") 
                    return redirect(url_for('dashboard.dashboard'))
                else:
                    print("Invalid password for email:", email)  
                    flash('Invalid email or password', 'danger')
            else:
                print("Email is not registered:", email)  
                flash('Invalid email or password', 'danger')

            cursor.close()
            close_db_connection(connection)
        else:
            flash('Error connecting to the database. Please try again later.', 'danger')

    return render_template('admin_login.html', title='Admin Log In', form=form)

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.landing'))

@auth_bp.route('/register/user', methods=['GET', 'POST'])
def register_user():
    form = UserRegistrationForm()

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

        send_user_verification_email(form.emailaddress.data, token)

        print("Student Number:", form.studno.data)
        print("First Name:", form.firstname.data)
        print("Last Name:", form.lastname.data)
        print("Email Address:", form.emailaddress.data)
        print("Contact Number:", form.contactnumber.data)
        print("Password:", form.password.data)
        print("License Plate Number:", form.license_number.data)
        print("Vehicle Model:", form.vehicle_model.data)
        flash_message = 'A verification email has been sent to your email address. Please verify your email to complete registration.'
        flash_link = url_for('auth.resend_user_verification_email')
        flash(flash_message, 'verification_success_message')
        flash(flash_link, 'flash_link')

        return redirect(url_for('auth.user_login'))

    return render_template('register_user.html', form=form)

@auth_bp.route('/resend_user_verification_email', methods=['GET'])
def resend_user_verification_email():
    email_address = session.get('registration_data', {}).get('email')

    if email_address:
        token = generate_verification_token()

        session['verification_token'] = token

        send_user_verification_email(email_address, token)

        flash('A verification email has been resent to your email address.', 'success')
        return redirect(url_for('auth.user_login'))

    else:
        flash('No email address found in the registration data. Please try registering again.', 'danger')

    return redirect(url_for('auth.register_user'))

@auth_bp.route('/verify_email/<token>', methods=['GET'])
def verify_user_email(token):
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

                qr_data = f"User ID: {user_id}\nStudent Number: {registration_data['studno']}\nLastname: {registration_data['lastname']}\nFirstname: {registration_data['firstname']}\nEmail: {registration_data['email']}\nContact Number: {registration_data['contactnumber']}"

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

@auth_bp.route('/register/admin', methods=['GET', 'POST'])
def register_admin():
    form = AdminRegistrationForm()

    if form.validate_on_submit():
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not recaptcha_response:
            flash('Please complete the reCAPTCHA challenge.', 'danger')
            return redirect(url_for('auth.register_admin'))

        recaptcha_secret_key = '6LfP-rUpAAAAAMfSpH2D0HIKxOodLKtgEi8Qxzdu'
        verification_url = 'https://www.google.com/recaptcha/api/siteverify'
        params = {
            'secret': recaptcha_secret_key,
            'response': recaptcha_response
        }
        response = requests.post(verification_url, data=params)
        if not response.json().get('success'):
            flash('reCAPTCHA verification failed. Please try again.', 'danger')
            return redirect(url_for('auth.register_admin'))

        password_hash = generate_password_hash(form.password.data)

        session['admin_registration_data'] = {
            'employee_id': form.employee_id.data,
            'firstname': form.firstname.data,
            'lastname': form.lastname.data,
            'email': form.email.data,
            'contactnumber': form.contactnumber.data, 
            'password': password_hash
        }

        token = generate_verification_token()
        session['verification_token'] = token

        send_admin_verification_email(form.email.data, token)

        flash_message = 'A verification email has been sent to your email address. Please verify your email to complete registration.'
        flash(flash_message, 'verification_success_message')
        return redirect(url_for('auth.admin_login'))

    return render_template('register_admin.html', form=form)

@auth_bp.route('/resend_admin_verification_email', methods=['GET'])
def resend_admin_verification_email():
    email_address = session.get('admin_registration_data', {}).get('email')

    if email_address:
        token = generate_verification_token()

        session['verification_token'] = token

        send_admin_verification_email(email_address, token)

        flash('A verification email has been resent to your email address.', 'success')
        return redirect(url_for('auth.admin_login'))

    else:
        flash('No email address found in the registration data. Please try registering again.', 'danger')

    return redirect(url_for('auth.register_admin'))

@auth_bp.route('/verify_admin_email/<token>', methods=['GET'])
def verify_admin_email(token):
    if verify_token(token):
        registration_data = session.get('admin_registration_data')

        if registration_data:
            try:
                cursor, connection = get_cursor()

                password_hash = registration_data['password']

                sql_admin = "INSERT INTO admin (employeeID, lastname, firstname, contactnumber, email, password) VALUES (%s, %s, %s, %s, %s, %s)"
                print("Executing SQL query:", sql_admin) 
                print("Data being inserted:", registration_data)  
                cursor.execute(sql_admin, (
                    registration_data['employee_id'],
                    registration_data['lastname'],
                    registration_data['firstname'],
                    registration_data['contactnumber'], 
                    registration_data['email'],
                    password_hash  
                ))
                connection.commit()

                flash('Your email has been verified. You can now log in.', 'success')
                cursor.close()
                close_db_connection(connection)
                session.pop('admin_registration_data')  
                print("Session data removed:", session.get('admin_registration_data')) 
                return redirect(url_for('auth.admin_login'))
            except mysql.connector.Error as err:
                print("Error executing SQL query:", err)  
                flash('Error registering admin: {}'.format(err), 'danger')
                cursor.close()
                close_db_connection(connection)
                return redirect(url_for('auth.admin_login'))
        else:
            print("No registration data found in session.")  
            flash('Registration data not found. Please try registering again.', 'danger')
            session.pop('admin_registration_data') 
            print("Session data removed:", session.get('admin_registration_data'))  
            return redirect(url_for('auth.admin_login'))
    else:
        print("Invalid or expired verification token.")  
        flash('Invalid or expired verification token.', 'danger')
        session.pop('admin_registration_data')  
        print("Session data removed:", session.get('admin_registration_data')) 
        return redirect(url_for('auth.admin_login'))


