from routes.auth_routes import auth_bp
from routes.timesheet_routes import timesheet_bp
from routes.analytics_routes import analytics_bp
from routes.user_routes import user_bp

__all__ = ['auth_bp', 'timesheet_bp', 'analytics_bp', 'user_bp']
