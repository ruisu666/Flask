import mysql.connector

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

def close_db_connection(connection):
    if connection:
        connection.close()

def execute_query(query, params=None, fetchone=False):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetchone:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        
        connection.commit()
        return result
    except mysql.connector.Error as err:
        print("Error executing query:", err)
        return None
    finally:
        cursor.close()
        close_db_connection(connection)
