from flask import Flask
from routes import klaim_bp

app = Flask(__name__)
app.secret_key = '12371237dfhdsf^&%44'
app.register_blueprint(klaim_bp)
# app.config['SECRET_KEY'] = 'your_secret_key'

if __name__ == '__main__':
    app.run(debug=True)
