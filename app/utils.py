import mysql.connector
from flask import session, flash, url_for
from flask_mail import Mail, Message
from app import app
import secrets
from werkzeug.security import generate_password_hash

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
        subject = "Verify Your Email Address"
        body = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Verification</title>
            <!-- Bootstrap CSS -->
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
            <!-- Custom CSS -->
            <style>
                .container {{
                    max-width: 600px;
                    margin: auto;
                    padding: 20px;
                }}
                .btn-verify {{
                    display: inline-block;
                    font-weight: 400;
                    color: #fff;
                    text-align: center;
                    vertical-align: middle;
                    user-select: none;
                    background-color: #007bff;
                    border: 1px solid transparent;
                    padding: 0.375rem 0.75rem;
                    font-size: 1rem;
                    line-height: 1.5;
                    border-radius: 0.25rem;
                    transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
                    text-decoration: none;
                }}
                .btn-verify:hover {{
                    color: #fff;
                    background-color: #0056b3;
                    border-color: #0056b3;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="text-center">Vehicle Management System</h1>
                <h2 class="text-center">Verify Your Email Address</h2>
                <p>Dear User,</p>
                <p>Click the following button to verify your email address:</p>
                <p><a href="{url_for('auth.verify_email', token=token, _external=True)}" class="btn btn-verify btn-lg">Verify Email</a></p>
                <p>Thank you!</p>
            </div>
        </body>
        </html>
        """
        message = Message(subject, recipients=[email], html=body)

        mail.send(message)
        return True  
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False  
    
def generate_verification_token():
    token = secrets.token_urlsafe(20)
    return token

def verify_token(token):
    if 'verification_token' in session and session['verification_token'] == token:
        session.pop('verification_token')
        return True
    else:
        return False

def send_recovery_email(email, token):
    try:
        # Create the recovery email message
        subject = "Reset Your Password"
        body = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset</title>
            <!-- Bootstrap CSS -->
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
            <!-- Custom CSS -->
            <style>
                /* CSS styles */
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="text-center">Vehicle Management System</h1>
                <h2 class="text-center">Reset Your Password</h2>
                <p>Dear User,</p>
                <p>You recently requested to reset your password. Click the following button to reset it:</p>
                <p><a href="{url_for('account_recovery.reset_password', token=token, email=email, _external=True)}" class="btn btn-reset btn-lg">Reset Password</a></p>
                <p>If you did not request a password reset, please ignore this email. This link is only valid for a limited time.</p>
                <p>Thank you!</p>
            </div>
        </body>
        </html>
        """
        message = Message(subject, recipients=[email], html=body)

        # Send the email
        mail.send(message)
        return True  
    except Exception as e:
        print(f"Error sending recovery email: {e}")
        return False 

def hash_password(password):
    """
    Hashes the given password using Werkzeug's generate_password_hash function.
    """
    hashed_password = generate_password_hash(password)
    return hashed_password
