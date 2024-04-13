from flask import Blueprint, request, session
from datetime import datetime
from app.utils import get_cursor, close_db_connection

record_bp = Blueprint('record', __name__)

@record_bp.route('/time_in_instructions', methods=['POST'])
def time_in_instructions():
    try:
        qr_data = request.form.get('qrData') 
        print("QR Data for Time In:", qr_data)
        save_qr_data(qr_data)
        
        # Retrieve current date and time
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Extract User ID from QR data
        user_id = extract_user_id(qr_data)
        
        # Check if user already timed in or is trying to time in again without timing out
        if is_user_timed_in(user_id) or is_user_same_status(user_id, time_in=True):
            return "User already timed in"
        
        # Log time in
        log_time_in(user_id, current_datetime)
        
        return "Instructions for Time In"
    except Exception as e:
        print("Error:", e)
        return "Error processing request", 500

@record_bp.route('/time_out_instructions', methods=['POST'])
def time_out_instructions():
    try:
        qr_data = request.form.get('qrData') 
        print("QR Data for Time Out:", qr_data)
        save_qr_data(qr_data)
        
        # Retrieve current date and time
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Extract User ID from QR data
        user_id = extract_user_id(qr_data)
        
        # Check if user already timed out or is trying to time out again without timing in
        if is_user_timed_out(user_id) or is_user_same_status(user_id, time_in=False):
            return "User already timed out"
        
        # Log time out
        log_time_out(user_id, current_datetime)
        
        return "Instructions for Time Out"
    except Exception as e:
        print("Error:", e)
        return "Error processing request", 500

def save_qr_data(qr_data):
    try:
        with open('qr_data.txt', 'w') as file:
            file.write(qr_data)
        print("QR Data saved successfully.")
    except Exception as e:
        print("Error saving QR Data:", e)

def extract_user_id(qr_data):
    # Assuming QR data is in a specific format and can be parsed to extract User ID
    # You need to implement the logic to extract the User ID from the QR data
    # For example:
    user_id = qr_data.split('\n')[0].split(': ')[1]
    return int(user_id)

def is_user_timed_in(user_id):
    try:
        cursor, connection = get_cursor()
        if cursor:
            sql = "SELECT * FROM time_logs WHERE userID = %s AND time_out IS NULL"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        print("Error checking time in status:", e)
    finally:
        close_db_connection(connection)

def is_user_timed_out(user_id):
    try:
        cursor, connection = get_cursor()
        if cursor:
            sql = "SELECT * FROM time_logs WHERE userID = %s AND time_out IS NOT NULL ORDER BY time_out DESC LIMIT 1"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        print("Error checking time out status:", e)
    finally:
        close_db_connection(connection)

def is_user_same_status(user_id, time_in):
    try:
        cursor, connection = get_cursor()
        if cursor:
            status_column = "time_in" if time_in else "time_out"
            sql = f"SELECT {status_column} FROM time_logs WHERE userID = %s ORDER BY time_in DESC LIMIT 1"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            # Check if the most recent entry has the same time_in or time_out status
            if result:
                return (time_in and result[status_column] is not None) or (not time_in and result[status_column] is None)
            else:
                return False
    except Exception as e:
        print("Error checking user status:", e)
    finally:
        close_db_connection(connection)


def log_time_in(user_id, current_datetime):
    try:
        cursor, connection = get_cursor()
        if cursor:
            sql = "INSERT INTO time_logs (userID, time_in) VALUES (%s, %s)"
            val = (user_id, current_datetime)
            cursor.execute(sql, val)
            connection.commit()
            print("Time in recorded successfully.")
    except Exception as e:
        print("Error logging time in:", e)
    finally:
        close_db_connection(connection)

def log_time_out(user_id, current_datetime):
    try:
        cursor, connection = get_cursor()
        if cursor:
            sql = "UPDATE time_logs SET time_out = %s WHERE userID = %s AND time_out IS NULL ORDER BY time_in DESC LIMIT 1"
            val = (current_datetime, user_id)
            cursor.execute(sql, val)
            connection.commit()
            print("Time out recorded successfully.")
    except Exception as e:
        print("Error logging time out:", e)
    finally:
        close_db_connection(connection)
