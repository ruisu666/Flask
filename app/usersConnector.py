from flask import render_template, Blueprint

users_bp = Blueprint('users', __name__)

@users_bp.route('/users')
def profile():
    return render_template('users.html')