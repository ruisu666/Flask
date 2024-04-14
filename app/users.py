from flask import render_template, flash, Blueprint, session, redirect, url_for, request
from app.utils import get_cursor, close_db_connection

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
def users():
    if 'user_role' not in session:
        flash('You are not logged in.', 'danger')
        return redirect(url_for('auth.landing'))

    user_role = session.get('user_role')
    if user_role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.landing'))

    page = request.args.get('page', 1, type=int) 
    per_page = 10  
    offset = (page - 1) * per_page

    try:
        cursor, connection = get_cursor()
        if cursor:
            # Querying users with pagination
            sql = """
                SELECT 
                    userinfo.studno, 
                    userinfo.lastname, 
                    userinfo.firstname, 
                    userinfo.email, 
                    userinfo.contactnumber
                FROM 
                    userinfo
                LIMIT {per_page} OFFSET {offset};
                """.format(per_page=per_page, offset=offset)

            print("Executing query:", sql)  
            cursor.execute(sql)
            users_info = cursor.fetchall()

            # Additional print statements
            print("Fetched users:", users_info)
            print("Users info before rendering template:", users_info)

            # Count total users
            cursor.execute("SELECT COUNT(*) FROM userinfo;")
            print("Executing count query: SELECT COUNT(*) FROM userinfo;")  
            total_users = cursor.fetchone()[0]
            total_pages = (total_users + per_page - 1) // per_page  
            return render_template('users.html', title='Users', user_role=user_role, users_info=users_info, page=page, total_pages=total_pages, per_page=per_page)  
    except Exception as e:
        print("Error fetching users:", e)
        flash("Error fetching users. Please try again later.", "danger")
    finally:
        if 'connection' in locals():
            close_db_connection(connection)

    return redirect(url_for('users.users', page=page))
