from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_caching import Cache
from market.config import Config


mail = Mail()
db = SQLAlchemy()
bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.login_view = 'users.login_page'
login_manager.login_message_category = "info"
login_manager.login_message = "Please Log in first"




def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.app_context().push()

    mail.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # cache = Cache(app, config={
    # 'CACHE_TYPE': 'SimpleCache',  # Options include: 'FileSystemCache', 'RedisCache', etc.
    # 'CACHE_DEFAULT_TIMEOUT': 300  # Default timeout in seconds
    # })
    # cache.init_app(app)
    
    from market.users.routes import users
    from market.items.routes import items
    from market.main.routes import main
    from market.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(items)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app 