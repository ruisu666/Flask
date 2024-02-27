from flask import Flask
from app.authConnector import auth_bp
from app.dashboardConnector import dashboard_bp
from app.profileConnector import profile_bp
from app.vehiclesConnector import vehicles_bp
from app.logsConnector import logs_bp

app = Flask(__name__)

app.config['SECRET_KEY'] = '3f664e5dcb9bcab8fbe6623969b6cf71383a9cbc21e40ef2019fb38952702d7b'

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(vehicles_bp)
app.register_blueprint(logs_bp)

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port=5000, debug=True )
