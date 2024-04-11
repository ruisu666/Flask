import base64
from flask import Blueprint, render_template, flash, redirect, url_for, session
from app.utils import get_cursor, close_db_connection
from pyzbar.pyzbar import decode
from PIL import Image
import io

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    # Check user role
    user_role = session.get('user_role')
    if user_role == 'admin':
        # Render admin dashboard
        adminID = session.get('adminID')
        if not adminID:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('auth.login'))
        return render_template('dashboard.html', user_role=user_role)  # Pass user_role to the template
    elif user_role == 'user':
        # Render user dashboard
        info_id = session.get('infoID')
        if not info_id:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('auth.login'))
        
        # Retrieve user's first name from the session
        user_firstname = session.get('user_firstname')
        
        # Retrieve QR code image data from the database
        cursor, connection = get_cursor()
        sql_get_qr_code = "SELECT qr_code_image FROM qr_codes WHERE userID = (SELECT userID FROM user WHERE infoID = %s)"
        cursor.execute(sql_get_qr_code, (info_id,))
        qr_code_image_base64 = cursor.fetchone()[0]  # Assuming only one QR code per user
        cursor.close()
        close_db_connection(connection)
        
        # Decode Base64 encoded QR code image
        qr_code_image_bytes = base64.b64decode(qr_code_image_base64)
        
        # Decode QR code image using pyzbar
        decoded_objects = decode(Image.open(io.BytesIO(qr_code_image_bytes)))
        decoded_data = [obj.data.decode('utf-8') for obj in decoded_objects]
        
        # Pass user_role, user_firstname, qr_code_image_base64, and decoded_data to the template
        return render_template('dashboard.html', user_role=user_role, user_firstname=user_firstname, qr_code_image=qr_code_image_base64, decoded_data=decoded_data)
    else:
        # Handle unknown user role
        flash('Please log in to access this page', 'danger')
        return redirect(url_for('auth.login'))
