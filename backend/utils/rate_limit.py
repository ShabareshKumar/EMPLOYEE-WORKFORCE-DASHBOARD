"""
Simple rate limiting decorator
"""
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Simple in-memory rate limit tracker
# In production, use Redis or similar
_rate_limit_store = {}

def rate_limit(max_requests=5, window_seconds=60):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier (IP address)
            client_id = request.remote_addr
            
            # Get current time
            now = datetime.now()
            
            # Clean up old entries
            cutoff = now - timedelta(seconds=window_seconds)
            if client_id in _rate_limit_store:
                _rate_limit_store[client_id] = [
                    timestamp for timestamp in _rate_limit_store[client_id]
                    if timestamp > cutoff
                ]
            
            # Check rate limit
            if client_id in _rate_limit_store:
                if len(_rate_limit_store[client_id]) >= max_requests:
                    logger.warning(f"Rate limit exceeded for {client_id}")
                    return jsonify({
                        'message': 'Rate limit exceeded. Please try again later.'
                    }), 429
            
            # Add current request
            if client_id not in _rate_limit_store:
                _rate_limit_store[client_id] = []
            _rate_limit_store[client_id].append(now)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
