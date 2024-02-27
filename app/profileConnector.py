from flask import render_template, Blueprint

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def profile():
    return render_template('profile.html')