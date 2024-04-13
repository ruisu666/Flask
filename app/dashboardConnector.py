import base64
import io
from flask import Blueprint, render_template, flash, redirect, url_for, session,request
from pyzbar.pyzbar import decode
from PIL import Image
from app.utils import get_cursor, close_db_connection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    user_role = session.get('user_role')
    decoded_data = session.get('decoded_data', '')  # Retrieve decoded data from session
    processed_route = f"/process_qr_code?qr_data={decoded_data}" if decoded_data else ""  # Define the processed route
    print("Decoded Data Admin:", decoded_data)
    #ADMIN SIDE
    if user_role == 'admin':
        adminID = session.get('adminID')
        if not adminID:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('auth.landing'))
        admin_firstname = session.get('admin_firstname')

        return render_template('dashboard.html', user_role=user_role, admin_firstname=admin_firstname, decoded_data=decoded_data, processed_route=processed_route)
    
    #USER SIDE
    elif user_role == 'user':
        info_id = session.get('infoID')
        if not info_id:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('auth.landing'))
        
        user_firstname = session.get('user_firstname')
        
        cursor, connection = get_cursor()
        try:
            sql_get_user_info = "SELECT studno,lastname,firstname,email,contactnumber FROM userinfo WHERE infoID = %s"
            cursor.execute(sql_get_user_info, (info_id,))
            user_info = cursor.fetchone()
            print("User Info:", user_info) 

            sql_get_vehicle_info = "SELECT * FROM vehicle WHERE userID = (SELECT userID FROM user WHERE infoID = %s)"
            cursor.execute(sql_get_vehicle_info, (info_id,))
            vehicle_info = cursor.fetchone()
            print("Vehicle Info:", vehicle_info) 

            sql_get_qr_code = "SELECT qr_code_image FROM qr_codes WHERE userID = (SELECT userID FROM user WHERE infoID = %s)"
            cursor.execute(sql_get_qr_code, (info_id,))
            qr_code_image_base64 = cursor.fetchone()[0]
            #print("QR Code Image:", qr_code_image_base64)  

            decoded_objects = decode(Image.open(io.BytesIO(base64.b64decode(qr_code_image_base64))))
            decoded_data = [obj.data.decode('utf-8') for obj in decoded_objects]
            print("Decoded Data:", decoded_data)  

        except Exception as e:
            flash(f'Error: {e}', 'danger')
            return redirect(url_for('auth.landing'))
        finally:
            cursor.close()
            close_db_connection(connection)
        
        return render_template('dashboard.html', user_role=user_role, user_firstname=user_firstname, user_info=user_info, vehicle_info=vehicle_info, qr_code_image=qr_code_image_base64, decoded_data=decoded_data)
    else:
        flash('Please log in to access this page', 'danger')
        return redirect(url_for('auth.landing'))
    
@dashboard_bp.route('/process_qr_code')
def process_qr_code():
    qr_data = request.args.get('qr_data')
    # Store the QR code data in session
    session['decoded_data'] = qr_data
    # Redirect back to the dashboard
    return redirect(url_for('dashboard.dashboard'))
