from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.utils import send_recovery_email, generate_verification_token, hash_password, get_db_connection, close_db_connection
from app.forms import AccountRecoveryForm, ResetPasswordForm
from werkzeug.security import generate_password_hash, check_password_hash

account_recovery_bp = Blueprint('account_recovery', __name__)

@account_recovery_bp.route('/account_recovery', methods=['GET', 'POST'])
def account_recovery():
    form = AccountRecoveryForm()

    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("SELECT email FROM userinfo WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                user_role = 'user'
            else:
                cursor.execute("SELECT email FROM admin WHERE email = %s", (email,))
                admin = cursor.fetchone()
                if admin:
                    user_role = 'admin'
                else:
                    close_db_connection(connection)
                    flash('This email address is not registered. Please enter a valid email address.', 'danger')
                    return redirect(url_for('account_recovery.account_recovery'))
            
            close_db_connection(connection)
            
            token = generate_verification_token()
            session['verification_token'] = token
            session['email'] = email
            session['user_role'] = user_role
            print("Session Data:", session)
            print("User Role:", user_role)
            send_recovery_email(email, token, user_role)
            flash('A recovery email has been sent to your email address. Please check your inbox to reset your password.', 'success')
            return redirect(url_for('account_recovery.account_recovery'))
        
        except Exception as e:
            print(f"Error during account recovery: {e}")
            flash('An error occurred during account recovery. Please try again later.', 'danger')
            return redirect(url_for('account_recovery.account_recovery'))

    return render_template('accountrecovery.html', title='Account Recovery', form=form)

@account_recovery_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    token = session.get('verification_token')
    email = session.get('email')
    user_role = session.get('user_role')
    print("User Role:", user_role)

    if request.method == 'POST' and form.validate_on_submit():
        password = form.password.data
        confirm_password = form.confirm_password.data

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('account_recovery.reset_password'))

        if token and email:
            try:
                connection = get_db_connection()
                cursor = connection.cursor()

                if user_role == 'user':
                    cursor.execute("SELECT password FROM userinfo WHERE email = %s", (email,))
                elif user_role == 'admin':
                    cursor.execute("SELECT password FROM admin WHERE email = %s", (email,))
                
                current_password_hash = cursor.fetchone()[0]

                if check_password_hash(current_password_hash, password):
                    flash('New password cannot be the same as the current password.', 'danger')
                    return redirect(url_for('account_recovery.reset_password'))

                hashed_password = generate_password_hash(password)

                if user_role == 'user':
                    update_query = "UPDATE userinfo SET password = %s WHERE email = %s"
                elif user_role == 'admin':
                    update_query = "UPDATE admin SET password = %s WHERE email = %s"

                cursor.execute(update_query, (hashed_password, email))
                connection.commit()

                flash('Password updated successfully.', 'success')
                session.pop('verification_token')
                session.pop('email')
                return redirect(url_for('auth.landing'))
            except Exception as e:
                print(f"Error updating password: {e}")
                flash('An error occurred while updating your password. Please try again later.', 'danger')
            finally:
                close_db_connection(connection)
        else:
            flash('Token or email not found in session. Please request a new password reset.', 'danger')

    return render_template('reset_password.html', title='Reset Password', form=form)

