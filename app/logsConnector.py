from flask import render_template, redirect, url_for, flash, session, Blueprint, request
from app.utils import get_cursor, close_db_connection

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/logs', methods=['GET'])
def logs():
    user_role = session.get('user_role')

    if user_role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    elif 'user_role' not in session: 
        flash('You are not logged in.', 'danger')
        return redirect(url_for('auth.landing'))
    
    page = request.args.get('page', 1, type=int)  

    try:
        cursor, connection = get_cursor()
        if cursor:
            sql = """
                    SELECT 
                        t.logID, 
                        ui.firstname, 
                        ui.lastname, 
                        ui.contactnumber, 
                        v.model, 
                        v.licenseplate, 
                        t.time_in, 
                        t.time_out
                    FROM 
                        time_logs t 
                    JOIN 
                        user u ON t.userID = u.userID 
                    JOIN 
                        userinfo ui ON u.infoID = ui.infoID
                    JOIN 
                        vehicle v ON u.userID = v.userID 
                    ORDER BY 
                        t.time_in DESC;

            """
            cursor.execute(sql)
            time_logs = cursor.fetchall()
            formatted_time_logs = []
            for log in time_logs:
                if len(log) >= 8: 
                    formatted_time_logs.append({
                        'logID': log[0],
                        'firstname': log[1],
                        'lastname': log[2],
                        'contactnumber': log[3],
                        # 'model': log[4],
                        # 'licenseplate': log[5],
                        'time_in': log[6],
                        'time_out': log[7],
                    })
                else:
                    print("Error: Incomplete log data:", log)
            return render_template('logs.html', title='Logs', user_role=user_role, time_logs=formatted_time_logs, page=page)  
    except Exception as e:
        print("Error fetching logs:", e)
        flash("Error fetching logs. Please try again later.", "danger")
    finally:
        if 'connection' in locals():
            close_db_connection(connection)

    return redirect(url_for('logs.logs', page=page))  
