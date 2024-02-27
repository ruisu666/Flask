import mysql.connector

# Connection details
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'vmsdb'
DB_PORT = 3306

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
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
