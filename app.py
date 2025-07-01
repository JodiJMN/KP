from flask import Flask
from routes import klaim_bp
from init import create_app

app = Flask(__name__)
# Import blueprint DI SINI
app.register_blueprint(klaim_bp)
# app.config['SECRET_KEY'] = 'your_secret_key'
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
