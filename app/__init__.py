from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from config.config import config

# Extensions
db            = SQLAlchemy()
login_manager = LoginManager()
mail          = Mail()
migrate       = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Bind extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Login manager settings
    login_manager.login_view         = 'auth.login'
    login_manager.login_message      = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    # User loader
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from app.auth.routes         import auth_bp
    from app.accounts.routes     import accounts_bp
    from app.transactions.routes import transactions_bp
    from app.loans.routes        import loans_bp
    from app.admin.routes        import admin_bp

    app.register_blueprint(auth_bp,          url_prefix='/auth')
    app.register_blueprint(accounts_bp,      url_prefix='/accounts')
    app.register_blueprint(transactions_bp,  url_prefix='/transactions')
    app.register_blueprint(loans_bp,         url_prefix='/loans')
    app.register_blueprint(admin_bp,         url_prefix='/admin')

    # Root redirect
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app