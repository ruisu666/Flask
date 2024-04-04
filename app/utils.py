import mysql.connector
from flask import session

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port='3306',
            user='root',
            password='',
            database='vmsdb'
        )
        return connection
    except mysql.connector.Error as err:
        print("Error connecting to MySQL database:", err)
        return None

def get_cursor():
    connection = get_db_connection()
    cursor = connection.cursor()
    return cursor, connection

def close_db_connection(connection):
    if connection:
        connection.close()

def logout_user():
    session.clear()