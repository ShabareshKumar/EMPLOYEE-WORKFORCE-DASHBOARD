from flask import Blueprint, request, jsonify
from models.database import db
from models.user import User
from utils.auth import token_required, role_required
from utils.validators import is_valid_email, validate_password, sanitize_text
from utils.demo_middleware import block_demo_access
import logging

user_bp = Blueprint('user', __name__)
logger = logging.getLogger(__name__)

@user_bp.route('/users', methods=['GET'])
@token_required
@role_required('admin', 'manager')
def get_users(current_user):
    """Get all users with pagination (excluding soft-deleted)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        # Query users, excluding soft-deleted by default
        query = User.query
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@user_bp.route('/users', methods=['POST'])
@token_required
@role_required('admin')
@block_demo_access
def create_user(current_user):
    """Create new user (admin only)"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'email', 'password', 'role']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Validate email format
        if not is_valid_email(data['email']):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        # Validate role
        valid_roles = ['admin', 'manager', 'employee']
        if data['role'] not in valid_roles:
            return jsonify({'message': f'Invalid role. Must be one of: {", ".join(valid_roles)}'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400
        
        # Sanitize inputs
        name = sanitize_text(data['name'], max_length=100)
        department = sanitize_text(data.get('department', ''), max_length=100)
        
        if not name:
            return jsonify({'message': 'Name cannot be empty'}), 400
        
        user = User(
            name=name,
            email=data['email'],
            role=data['role'],
            department=department
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@user_bp.route('/users/<int:id>', methods=['PUT'])
@token_required
@role_required('admin')
@block_demo_access
def update_user(current_user, id):
    """Update user (admin only)"""
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            name = sanitize_text(data['name'], max_length=100)
            if not name:
                return jsonify({'message': 'Name cannot be empty'}), 400
            user.name = name
        
        if 'email' in data:
            if not is_valid_email(data['email']):
                return jsonify({'message': 'Invalid email format'}), 400
            if User.query.filter(User.email == data['email'], User.id != id).first():
                return jsonify({'message': 'Email already exists'}), 400
            user.email = data['email']
        
        if 'role' in data:
            valid_roles = ['admin', 'manager', 'employee']
            if data['role'] not in valid_roles:
                return jsonify({'message': f'Invalid role. Must be one of: {", ".join(valid_roles)}'}), 400
            user.role = data['role']
        
        if 'department' in data:
            user.department = sanitize_text(data['department'], max_length=100)
        
        if 'password' in data:
            is_valid, message = validate_password(data['password'])
            if not is_valid:
                return jsonify({'message': message}), 400
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@user_bp.route('/users/<int:id>', methods=['DELETE'])
@token_required
@role_required('admin')
@block_demo_access
def delete_user(current_user, id):
    """Soft delete user (admin only)"""
    try:
        user = User.query.get(id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Prevent deleting yourself
        if user.id == current_user.id:
            return jsonify({'message': 'Cannot delete your own account'}), 400
        
        # Soft delete
        user.soft_delete()
        db.session.commit()
        
        logger.info(f"User {user.email} soft deleted by {current_user.email}")
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting user: {str(e)}")
        return jsonify({'message': 'An error occurred while deleting user'}), 500

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get current user profile"""
    return jsonify({'user': current_user.to_dict()}), 200
