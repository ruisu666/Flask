import os
from OpenSSL import crypto
from flask import Flask
from app.authConnector import auth_bp
from app.dashboardConnector import dashboard_bp
from app.logsConnector import logs_bp
from app.accountrecovery import account_recovery_bp 
from app.profile import profile_bp
from app.vehicles import vehicles_bp
from flask_mail import Mail
from app.record import record_bp
from app.users import users_bp

# Get the directory of the current script
current_dir = os.path.dirname(__file__)
cert_path = os.path.join(current_dir, "cert.pem")
key_path = os.path.join(current_dir, "key.pem")

# Generate SSL certificate and key if they don't exist
if not (os.path.isfile(cert_path) and os.path.isfile(key_path)):
    # Generate SSL certificate and key
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    cert = crypto.X509()
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)  # Valid for 1 year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    # Save certificate and key to files
    with open(cert_path, "wb") as cert_file:
        cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open(key_path, "wb") as key_file:
        key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465  
app.config['MAIL_USE_SSL'] = True  
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'e.luis.pelaez@gmail.com'

mail = Mail(app)

app.config['SECRET_KEY'] = '3f664e5dcb9bcab8fbe6623969b6cf71383a9cbc21e40ef2019fb38952702d7b'

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(account_recovery_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(vehicles_bp)
app.register_blueprint(record_bp)
app.register_blueprint(users_bp)

if __name__ == "__main__":
    # Use the SSL certificate and private key files
    ssl_context = (cert_path, key_path)
    app.run(host='0.0.0.0', port=3000, debug=True, ssl_context=ssl_context)
