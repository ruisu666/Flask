from flask import Blueprint, render_template, flash, redirect, url_for, session, request
from app.utils import get_cursor, close_db_connection
import mysql.connector
import qrcode
import base64
import io

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'infoID' not in session or session.get('user_role') != 'user':
        flash('You must be logged in as a user to access this page.', 'danger')
        return redirect(url_for('auth.login'))

    try:
        cursor, connection = get_cursor()
        info_id = session['infoID']

        if request.method == 'POST':
            # Get form data
            form_data = {
                'studno': request.form['studno'],
                'lastname': request.form['lastname'],
                'firstname': request.form['firstname'],
                'email': request.form['email'],
                'contactnumber': request.form['contactnumber'],
                'licenseplate': request.form['license_number'],
                'model': request.form['vehicle_model']
            }

            # Update user information
            if update_user_info(info_id, form_data):
                # If user information is updated successfully, update QR code
                if update_qr_code(info_id, form_data):
                    flash('Profile updated successfully!', 'success')
                else:
                    flash('Error updating QR code.', 'danger')
            else:
                flash('Error updating user information.', 'danger')

            cursor.close()
            close_db_connection(connection)

            # Redirect to the profile page
            return redirect(url_for('profile.profile'))

        # Fetch user information
        query = "SELECT * FROM userinfo WHERE infoID = %s"
        cursor.execute(query, (info_id,))
        user_info = cursor.fetchone()

        cursor.close()
        close_db_connection(connection)

        return render_template('profile.html', title='Profile', user_info=user_info)
    
    except mysql.connector.Error as err:
        flash('Error accessing database: {}'.format(err), 'danger')
        cursor.close()
        close_db_connection(connection)
        return redirect(url_for('auth.login'))

def update_user_info(info_id, form_data):
    try:
        cursor, connection = get_cursor()
        # Update the userinfo table with the new form data
        update_query = """
        UPDATE userinfo
        SET studno = %s, lastname = %s, firstname = %s, email = %s, contactnumber = %s
        WHERE infoID = %s
        """
        cursor.execute(update_query, (
            form_data['studno'],
            form_data['lastname'],
            form_data['firstname'],
            form_data['email'],
            form_data['contactnumber'],
            info_id
        ))
        connection.commit()
        cursor.close()
        close_db_connection(connection)
        return True
    except Exception as e:
        print(f"Error updating user information: {e}")
        return False

def update_qr_code(info_id, form_data):
    try:
        # Generate QR code image based on user info
        qr_data = f"Name: {form_data['firstname']} {form_data['lastname']}\nEmail: {form_data['email']}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Convert QR code image to base64 format
        buffered = io.BytesIO()
        qr_img.save(buffered, format="PNG")
        qr_img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Update the qr_codes table with the new QR code image
        cursor, connection = get_cursor()
        update_query = """
        UPDATE qr_codes
        SET qr_code_image = %s
        WHERE userID = (SELECT userID FROM userinfo WHERE infoID = %s)
        """
        cursor.execute(update_query, (qr_img_str, info_id))
        connection.commit()
        cursor.close()
        close_db_connection(connection)
        return True
    except Exception as e:
        print(f"Error updating QR code: {e}")
        return False
