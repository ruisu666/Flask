from flask import Flask
from app.auth import auth_bp
from app.routes import routes_bp

app = Flask(__name__)

app.config['SECRET_KEY'] = '3f664e5dcb9bcab8fbe6623969b6cf71383a9cbc21e40ef2019fb38952702d7b'

app.register_blueprint(auth_bp)
app.register_blueprint(routes_bp)

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port=5000, debug=True )
