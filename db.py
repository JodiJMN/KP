from flask_mysqldb import MySQL
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='db_claim'
    )