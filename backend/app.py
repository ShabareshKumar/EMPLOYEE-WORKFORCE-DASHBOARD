import os
import logging
import uuid
from logging.handlers import RotatingFileHandler
from flask import Flask, g, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from config import Config
from models.database import db, init_db
from routes.auth_routes import auth_bp
from routes.timesheet_routes import timesheet_bp
from routes.analytics_routes import analytics_bp
from routes.user_routes import user_bp
from routes.project_routes import project_bp

# Initialize extensions
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

csrf = CSRFProtect()

def setup_logging(app):
    """Configure application logging"""
    if not app.debug:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler for errors
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')
    else:
        # Console logging for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.DEBUG)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Validate configuration
    Config.init_app()
    
    # Setup logging
    setup_logging(app)
    
    # Initialize rate limiter
    limiter.init_app(app)
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Request tracing middleware
    @app.before_request
    def add_request_id():
        """Add unique request ID for tracing"""
        g.request_id = str(uuid.uuid4())
        app.logger.info(f"Request {g.request_id}: {request.method} {request.path}")
    
    @app.after_request
    def log_response(response):
        """Log response status"""
        app.logger.info(f"Response {g.request_id}: {response.status_code}")
        return response
    
    # Enable CORS with environment-based configuration
    if app.config['DEBUG']:
        # Development: Allow all origins
        CORS(app, resources={r"/api/*": {"origins": "*"}})
        app.logger.warning("⚠️  CORS: Allowing all origins (DEVELOPMENT MODE ONLY)")
    else:
        # Production: Restrict to specific origins
        allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
        allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
        
        if not allowed_origins:
            app.logger.error("❌ ALLOWED_ORIGINS not set in production!")
            raise ValueError("ALLOWED_ORIGINS environment variable must be set in production!")
        
        CORS(app, resources={
            r"/api/*": {
                "origins": allowed_origins,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True
            }
        })
        app.logger.info(f"✅ CORS: Restricted to origins: {allowed_origins}")
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        init_db()
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(timesheet_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(project_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring"""
        try:
            from datetime import datetime, timezone
            # Check database connection
            db.session.execute(db.text('SELECT 1'))
            return {
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, 200
        except Exception as e:
            app.logger.error(f'Health check failed: {str(e)}')
            return {
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e)
            }, 503
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f'404 error: {error}')
        return {'message': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'500 error: {error}', exc_info=True)
        db.session.rollback()
        return {'message': 'Internal server error'}, 500
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        app.logger.warning(f'Rate limit exceeded: {error}')
        return {'message': 'Rate limit exceeded. Please try again later.'}, 429
    
    app.logger.info('Application initialized successfully')
    return app

if __name__ == '__main__':
    app = create_app()
    # debug=True only when DEBUG env var is explicitly True (local dev only)
    # In production, gunicorn is used — this block never runs
    is_debug = os.getenv('DEBUG', 'False').strip().lower() in ('true', '1', 'yes')
    app.run(debug=is_debug, port=5000)
