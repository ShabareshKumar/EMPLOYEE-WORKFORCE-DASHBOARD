from flask import Blueprint, request, jsonify
from models.database import db
from models.user import User
from utils.validators import is_valid_email, validate_password, sanitize_text
from utils.rate_limit import rate_limit
from utils.demo_middleware import is_demo_user
import jwt
from datetime import datetime, timedelta, timezone
from config import Config
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=60)
def login():
    """User login endpoint with strict rate limiting (5 attempts per minute)"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password required'}), 400
        
        # Validate email format
        if not is_valid_email(data['email']):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            logger.warning(f"Failed login attempt for email: {data['email']}")
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Check if user is deleted
        if user.is_deleted:
            logger.warning(f"Login attempt for deleted user: {data['email']}")
            return jsonify({'message': 'Account not found'}), 401
        
        # Generate JWT token with 1 hour expiration (PRODUCTION SECURITY)
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1)
        }, Config.JWT_SECRET_KEY, algorithm='HS256')
        
        logger.info(f"Successful login for user: {user.email}")
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except jwt.PyJWTError as e:
        logger.error(f"JWT error during login: {str(e)}")
        return jsonify({'message': 'Authentication error'}), 500
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'An error occurred during login'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Sanitize inputs
        name = sanitize_text(data['name'], max_length=100)
        email = data['email'].strip().lower()
        department = sanitize_text(data.get('department', ''), max_length=100)
        
        # Validate email format
        if not is_valid_email(email):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            name=name,
            email=email,
            role=data.get('role', 'employee'),
            department=department
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user registered: {user.email}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'message': 'An error occurred during registration'}), 500
