from flask import Blueprint
from flask import render_template
# from market import cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


main = Blueprint('main', __name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]  # Set rate limits globally
)

@main.route('/')
@main.route('/home')
# @cache.cached(timeout=300)
@limiter.limit("100 per minute")
def home_page():
    return render_template('home.html')
