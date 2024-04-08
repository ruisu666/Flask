import mysql.connector
from flask import session, flash, url_for
from flask_mail import Mail, Message
from app import app
import secrets

mail = Mail(app)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port='3306',
            user='root',
            password='',
            database='vmsdb'
        )
        return connection
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.CR_CONNECTION_ERROR:
            print("Error: XAMPP connection is closed or MySQL service is not running.")
            flash("Error: XAMPP connection is closed or MySQL service is not running.", "danger")
        else:
            print("Error connecting to MySQL database:", err)
            flash("Error connecting to MySQL database. Please try again later.", "danger")
        return None

def get_cursor():
    connection = get_db_connection()
    cursor = connection.cursor()
    return cursor, connection

def close_db_connection(connection):
    if connection:
        connection.close()

def logout_user():
    session.clear()

def log_in_user(user, user_id, user_role):
    session["user"] = user
    session["user_id"] = user_id
    session["user_role"] = user_role

def is_user_logged_in():
    return "user_id" in session

def get_current_user_data():
    user = session.get("user")
    user_id = session.get("user_id")
    return user, user_id

def send_verification_email(email, token):
    try:
        # Create the verification email message
        subject = "Verify Your Email Address"
        body = f"""
        <p>Dear User,</p>
        <p>Click the following link to verify your email address:</p>
        <p><a href="{url_for('auth.verify_email', token=token, _external=True)}">Verify Email</a></p>
        <p>Thank you!</p>
        """
        message = Message(subject, recipients=[email], html=body)

        # Send the email
        mail.send(message)
        return True  # Email sent successfully
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False  # Failed to send email

def generate_verification_token():
    # Generate a random 20-character token
    token = secrets.token_urlsafe(20)
    return token

def verify_token(token):
    # Check if the token exists in the session
    if 'verification_token' in session and session['verification_token'] == token:
        # If the token exists and matches, remove it from the session
        session.pop('verification_token')
        return True
    else:
        # If the token does not exist or does not match, return False
        return False
