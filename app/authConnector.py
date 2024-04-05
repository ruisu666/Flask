from flask import Blueprint, render_template, flash, redirect, url_for, session, request
from app.forms import LoginForm, RegistrationForm
from app.utils import (
    get_cursor,
    get_db_connection,
    close_db_connection,
    logout_user
)
import mysql.connector 
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.userlogin'))

@auth_bp.route('/login/user', methods=['GET', 'POST'])
def userlogin():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        try:
            cursor, connection = get_cursor()
        except AttributeError:
            flash('Error connecting to the database. Please try again later.', 'danger')
            return redirect(url_for('auth.userlogin'))
        
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
                return redirect(url_for('dashboard.userdashboard'))
            else:
                flash('Login unsuccessful. Please check username and password', 'danger')
                cursor.close()
                close_db_connection(connection)

        else:
            flash('Error connecting to the database. Please try again later.', 'danger')
            return redirect(url_for('auth.userlogin'))
    
    return render_template('userlogin.html', title='Log In', form=form)

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
                return redirect(url_for('dashboard.userdashboard'))
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
        return redirect(url_for('auth.userlogin'))  
    else:
        return render_template("userlogin.html")


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
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
                # Insert user info into userinfo table
                sql = "INSERT INTO userinfo (lastname, firstname, email, contactnumber, password) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (lastname, firstname, emailaddress, contactnumber, password))
                connection.commit()

                # Get the userID of the inserted user
                userID = cursor.lastrowid

                # Insert vehicle info into vehicle table
                sql = "INSERT INTO vehicle (userID, licenseplate, model) VALUES (%s, %s, %s)"
                cursor.execute(sql, (userID, licenseplate, model))
                connection.commit()

                flash('Registration successful!', 'success')
                cursor.close()
                close_db_connection(connection)
                return redirect(url_for('auth.userlogin'))

            except mysql.connector.Error as err:
                flash('Error registering user or vehicle: {}'.format(err), 'danger')
                cursor.close()
                close_db_connection(connection)
                return redirect(url_for('auth.register'))

        else:
            flash('Error connecting to the database. Please try again later.', 'danger')

    return render_template('register.html', form=form)
