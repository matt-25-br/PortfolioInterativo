import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://localhost/portfolio")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Upload configuration
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # CSRF configuration - disable for AJAX endpoints
    
    # Login manager configuration
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Por favor, faça login para acessar esta página."
    login_manager.login_message_category = "info"
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Create upload directory
    upload_dir = app.config["UPLOAD_FOLDER"]
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # Create database tables
    with app.app_context():
        import models
        db.create_all()
        
        # Create owner user if it doesn't exist
        from models import User
        from werkzeug.security import generate_password_hash
        
        owner = User.query.filter_by(is_owner=True).first()
        if not owner:
            owner = User()
            owner.username = "admin"
            owner.email = "admin@portfolio.com"
            owner.name = "Administrador"
            owner.password_hash = generate_password_hash("admin123")
            owner.is_owner = True
            db.session.add(owner)
            db.session.commit()
            logging.info("Owner user created: admin/admin123")
    
    # Register blueprints
    from routes import main_bp, auth_bp, owner_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(owner_bp, url_prefix="/owner")
    
    return app

# Create app instance
app = create_app()
