"""
Demo account middleware and restrictions
"""
from functools import wraps
from flask import jsonify

def block_demo_access(func):
    """Decorator to block demo users from accessing certain endpoints"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get current_user from kwargs (passed by token_required decorator)
        current_user = kwargs.get('current_user')
        
        if current_user and hasattr(current_user, 'is_demo') and current_user.is_demo:
            return jsonify({
                'message': 'Demo account has limited access. This action is not available for demo users.'
            }), 403
        
        return func(*args, **kwargs)
    
    return wrapper

def is_demo_user(user):
    """Check if user is a demo account"""
    return hasattr(user, 'is_demo') and user.is_demo
