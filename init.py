from flask import Flask, g
from flask_mail import Mail
from datetime import datetime, timedelta
from db import get_connection
from flask_bcrypt import Bcrypt
from utils import get_due_soon_claims, format_rupiah

bcrypt = Bcrypt()
mail = Mail()
app = Flask(__name__)

def create_app():
    app.secret_key = '12371237dfhdsf^&%44'
    app.permanent_session_lifetime = timedelta(minutes=60)
    # app.register_blueprint(klaim_bp)
    
    # Konfigurasi Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'chatgptkw1@gmail.com'
    app.config['MAIL_PASSWORD'] = 'iojsrwmtzsnmmomd'
    
    mail.init_app(app)

    # Import blueprint DI SINI
    from routes import klaim_bp
    app.register_blueprint(klaim_bp)
    bcrypt.init_app(app)

    return app

@app.context_processor
def inject_footer_data():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tb_user")
        result = cursor.fetchone()
        total_users = result[0] if result else 0
        cursor.close()
        conn.close()
    except Exception as e:
        total_users = 0  # fallback jika error DB
    return {
        'current_year': datetime.now().year,
        'total_users': total_users,
        'due_soon_claims': get_due_soon_claims(),
        'format_rupiah': format_rupiah,
    }
    

