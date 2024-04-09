from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.utils import get_cursor, close_db_connection, send_verification_email, generate_verification_token, send_recovery_email
from app.forms import AccountRecoveryForm

account_recovery_bp = Blueprint('account_recovery', __name__)

@account_recovery_bp.route('/account_recovery', methods=['GET', 'POST'])
def account_recovery():
    form = AccountRecoveryForm()  # Create an instance of the form

    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        
        # Check if the email exists in the database
        try:
            cursor, connection = get_cursor()
            query = "SELECT * FROM userinfo WHERE email = %s"
            cursor.execute(query, (email,))
            user_info = cursor.fetchone()
            cursor.close()
            close_db_connection(connection)
            
            if user_info:
                # Generate a verification token and send recovery email
                token = generate_verification_token()
                session['verification_token'] = token
                send_recovery_email(email, token)  # Send recovery email instead of verification email
                flash('A recovery email has been sent to your email address. Please check your inbox to reset your password.', 'success')
            else:
                flash('No user found with that email address. Please try again.', 'danger')
        except Exception as e:
            flash('An error occurred. Please try again later.', 'danger')
    
    return render_template('accountrecovery.html', title='Account Recovery', form=form)
