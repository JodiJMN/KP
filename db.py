import os
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME')
    )
    
# class Config :
#     #Secret Key
#     SECRET_KEY = os.environ.get('SECRET KEY') or '12371237dfhdsf^&%44'
    
#     # MySQL Configuration
#     MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
#     MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
#     MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or '' # Kosongkan jika tidak ada password
#     MYSQL_DB = os.environ.get('MYSQL_DB') or 'db_claim'
#     MYSQL_CURSORCLASS = 'DictCursor'  # Menggunakan DictCursor untuk hasil query sebagai dictionary
    
#     # Flask-Mail Configuration
#     MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
#     MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
#     MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
#     MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'chatgptkw1@gmail.com'
#     MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'Calang45'
#     MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME

