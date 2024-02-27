from flask import render_template, Blueprint

vehicles_bp = Blueprint('vehicles', __name__)

@vehicles_bp.route('/vehicles')
def profile():
    return render_template('vehicles.html')