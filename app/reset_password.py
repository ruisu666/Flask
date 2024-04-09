from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.utils import get_cursor, close_db_connection
from app.forms import ResetPasswordForm

reset_password_bp = Blueprint('reset_password', __name__)

@reset_password_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()  # Create an instance of the form

    if request.method == 'POST' and form.validate_on_submit():
        # Process the form submission
        password = form.password.data
        confirm_password = form.confirm_password.data

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('reset_password.reset_password'))

        # Get current user ID from session
        user_id = session.get('user_id')

        # Update password in the database
        try:
            cursor, connection = get_cursor()
            query = "UPDATE users SET password = %s WHERE id = %s"
            cursor.execute(query, (password, user_id))
            connection.commit()
            cursor.close()
            close_db_connection(connection)
            flash('Password updated successfully.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('An error occurred while updating the password. Please try again later.', 'danger')
            print(f"Error updating password: {e}")

    return render_template('reset_password.html', title='Reset Password', form=form)
