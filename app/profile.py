from flask import Blueprint, render_template, flash, redirect, url_for, session, request
from app.utils import get_cursor, close_db_connection

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/edit/student_number', methods=['GET', 'POST'])
def edit_student_number():
    if request.method == 'POST':
        new_student_number = request.form['student_number']
        
        cursor, connection = get_cursor()
        try:
            sql_update_student_number = "UPDATE userinfo SET studno = %s WHERE infoID = %s"
            cursor.execute(sql_update_student_number, (new_student_number, session.get('infoID')))
            connection.commit()
            flash('Student number updated successfully!', 'success') 
        except Exception as e:
            connection.rollback()  
            flash(f'Error updating student number: {e}', 'danger')  
        finally:
            cursor.close() 
            close_db_connection(connection)  
        
        return redirect(url_for('dashboard.dashboard'))  
    else:
        flash("something happened",'danger')
        return render_template('dashboard.dashboard')

