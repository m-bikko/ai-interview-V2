import os
from flask import Flask, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
migrate = Migrate()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable more verbose error messages for debugging
    app.config['PROPAGATE_EXCEPTIONS'] = True
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    
    # Create upload directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CV_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROFILE_PICS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)
    
    # Register Jinja filters
    from app.jinja_filters import register_filters
    register_filters(app)
    
    # Register blueprints
    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.catalog import catalog
    from app.routes.interview import interview
    from app.routes.history import history
    from app.routes.cv import cv
    from app.routes.profile import profile
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(catalog)
    app.register_blueprint(interview)
    app.register_blueprint(history)
    app.register_blueprint(cv)
    app.register_blueprint(profile)
    
    # Configure Gemini API
    from app.services.gemini_service import configure_gemini
    configure_gemini()
    
    # Middleware to check UI preference
    @app.after_request
    def check_ui_preference(response):
        # Check if the ui_preference parameter was passed in the query string
        ui_preference = request.args.get('ui')
        if ui_preference in ['modern', 'original']:
            # Set the cookie if a valid preference was provided
            response.set_cookie('ai_interview_ui', ui_preference, max_age=30*24*60*60)  # 30 days
        return response
    
    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404
        
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
        
    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html'), 500
    
    return app

from app import models