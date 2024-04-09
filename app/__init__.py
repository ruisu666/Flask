from flask import Flask
from flask_mail import Mail
import os

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')

mail = Mail(app)

app.config['SECRET_KEY'] = 'your_secret_key'

# Comment out the blueprint registrations
# from app.authConnector import auth_bp
# from app.dashboardConnector import dashboard_bp
# from app.logsConnector import logs_bp
# from app.vehiclesConnector import vehicles_bp

# app.register_blueprint(auth_bp)
# app.register_blueprint(dashboard_bp)
# app.register_blueprint(logs_bp)
# app.register_blueprint(vehicles_bp)
