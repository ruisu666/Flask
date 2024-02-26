from flask import Blueprint, render_template

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
def home():
    return render_template('home.html')

@routes_bp.route('/about')
def about():
    return render_template('about.html')
