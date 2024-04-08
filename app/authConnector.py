from flask import Blueprint, render_template, flash, redirect, url_for, session
from app.forms import LoginForm, RegistrationForm
from app.utils import get_cursor, close_db_connection, logout_user, log_in_user
import mysql.connector 
from app.dashboardConnector import dashboard_bp 

auth_bp = Blueprint('auth', __name__)

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

            if admin_info and password == admin_info[1]:
                admin_id = admin_info[0]
                session['adminID'] = admin_id
                session['user_role'] = 'admin'
                flash('Admin login successful!', 'success')
                cursor.close()
                close_db_connection(connection)
                return redirect(url_for('dashboard.dashboard'))

            # Check if the email exists in the userinfo table
            query = "SELECT infoID, password FROM userinfo WHERE email = %s"
            cursor.execute(query, (email,))
            user_info = cursor.fetchone()

            if user_info and password == user_info[1]:
                info_id = user_info[0]
                session['infoID'] = info_id
                session['user_role'] = 'user'
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
        studno = form.studno.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        emailaddress = form.emailaddress.data
        contactnumber = form.contactnumber.data
        password = form.password.data
        licenseplate = form.license_number.data
        model = form.vehicle_model.data

        try:
            cursor, connection = get_cursor()
        except AttributeError:
            flash('Error connecting to the database. Please try again later.', 'danger')
            return redirect(url_for('auth.register'))

        if connection is not None:
            try:
                # Inserting data into the database
                sql_userinfo = "INSERT INTO userinfo (studno, lastname, firstname, email, contactnumber, password) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql_userinfo, (studno, lastname, firstname, emailaddress, contactnumber, password))
                connection.commit()

                userID = cursor.lastrowid

                sql_vehicle = "INSERT INTO vehicle (userID, licenseplate, model) VALUES (%s, %s, %s)"
                cursor.execute(sql_vehicle, (userID, licenseplate, model))
                connection.commit()

                flash('Registration successful! Please check your email to verify your email address and complete the registration.', 'success') 
                cursor.close()
                close_db_connection(connection)
                return redirect(url_for('auth.login')) 

            except mysql.connector.Error as err:
                flash('Error registering user or vehicle: {}'.format(err), 'danger')
                cursor.close()
                close_db_connection(connection)
                return redirect(url_for('auth.register'))

        else:
            flash('Error connecting to the database. Please try again later.', 'danger')

    return render_template('register.html', form=form)
