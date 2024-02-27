from flask import render_template, Blueprint

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/logs')
def profile():
    return render_template('logs.html')