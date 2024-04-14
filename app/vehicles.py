import mysql.connector
from flask import flash, render_template, Blueprint
from app.utils import close_db_connection, get_db_connection


vehicles_bp = Blueprint('vehicles', __name__)

@vehicles_bp.route('/myvehicles')
def vehicles():
    vehicles = get_all_vehicles()
    if vehicles is None:
        flash("Failed to fetch vehicles.", "danger")
        return render_template('vehicles.html', title='Vehicles', vehicles=[])
    else:
        return render_template('vehicles.html', title='Vehicles', vehicles=vehicles)

def get_all_vehicles():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vehicle")
        vehicles = cursor.fetchall()
        return vehicles
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.CR_CONNECTION_ERROR:
            print("Error: XAMPP connection is closed or MySQL service is not running.")
            flash("Error: XAMPP connection is closed or MySQL service is not running.", "danger")
        else:
            print("Error fetching vehicles:", err)
            flash("Error fetching vehicles. Please try again later.", "danger")
        return None
    finally:
        close_db_connection(connection)
