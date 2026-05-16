from flask import Blueprint, request, jsonify
from models.database import db
from models.timesheet import Timesheet
from utils.auth import token_required
from utils.validators import validate_hours, sanitize_text
from utils.demo_middleware import block_demo_access
from datetime import datetime
import logging

timesheet_bp = Blueprint('timesheet', __name__)
logger = logging.getLogger(__name__)

@timesheet_bp.route('/timesheets', methods=['GET'])
@token_required
def get_timesheets(current_user):
    """Get timesheets for current user or all (for managers/admins) with pagination"""
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        # Managers and admins can see all timesheets
        if current_user.role in ['admin', 'manager']:
            user_id = request.args.get('user_id')
            if user_id:
                query = Timesheet.query.filter_by(user_id=user_id)
            else:
                query = Timesheet.query
        else:
            # Employees see only their own
            query = Timesheet.query.filter_by(user_id=current_user.id)
        
        # Order by date descending
        query = query.order_by(Timesheet.date.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'timesheets': [t.to_dict() for t in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@timesheet_bp.route('/timesheets', methods=['POST'])
@token_required
@block_demo_access
def create_timesheet(current_user):
    """Create new timesheet entry"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['date', 'productive_hours', 'non_productive_hours']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Validate hours
        is_valid, message = validate_hours(data['productive_hours'], data['non_productive_hours'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        # Check if using new structured format or legacy format
        if data.get('project_id'):
            # New structured format
            if not data.get('category_id') or not data.get('task_id'):
                return jsonify({'message': 'Category and task are required for structured projects'}), 400
            
            # Check for duplicate timesheet (structured format)
            existing = Timesheet.query.filter_by(
                user_id=current_user.id,
                date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                project_id=data['project_id'],
                category_id=data['category_id'],
                task_id=data['task_id']
            ).first()
            
            if existing:
                return jsonify({'message': 'Duplicate timesheet entry for this date, project, category, and task'}), 400
            
            timesheet = Timesheet(
                user_id=current_user.id,
                date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                project_id=data['project_id'],
                category_id=data['category_id'],
                task_id=data['task_id'],
                productive_hours=float(data['productive_hours']),
                non_productive_hours=float(data['non_productive_hours']),
                description=sanitize_text(data.get('description', ''), max_length=500)
            )
        else:
            # Legacy format (backward compatibility)
            if not data.get('project') or not data.get('task'):
                return jsonify({'message': 'Project and task are required'}), 400
            
            project = sanitize_text(data['project'], max_length=200)
            task = sanitize_text(data['task'], max_length=200)
            
            if not project or not task:
                return jsonify({'message': 'Project and task cannot be empty'}), 400
            
            # Check for duplicate timesheet (legacy format)
            existing = Timesheet.query.filter_by(
                user_id=current_user.id,
                date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                project=project,
                task=task
            ).first()
            
            if existing:
                return jsonify({'message': 'Duplicate timesheet entry for this date, project, and task'}), 400
            
            timesheet = Timesheet(
                user_id=current_user.id,
                date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                project=project,
                task=task,
                productive_hours=float(data['productive_hours']),
                non_productive_hours=float(data['non_productive_hours']),
                description=sanitize_text(data.get('description', ''), max_length=500)
            )
        
        db.session.add(timesheet)
        db.session.commit()
        
        return jsonify({
            'message': 'Timesheet created successfully',
            'timesheet': timesheet.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@timesheet_bp.route('/timesheets/<int:id>', methods=['PUT'])
@token_required
@block_demo_access
def update_timesheet(current_user, id):
    """Update timesheet entry"""
    try:
        timesheet = Timesheet.query.get(id)
        
        if not timesheet:
            return jsonify({'message': 'Timesheet not found'}), 404
        
        # Check ownership
        if timesheet.user_id != current_user.id and current_user.role not in ['admin', 'manager']:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'date' in data:
            try:
                timesheet.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        if 'project' in data:
            project = sanitize_text(data['project'], max_length=200)
            if not project:
                return jsonify({'message': 'Project cannot be empty'}), 400
            timesheet.project = project
        
        if 'task' in data:
            task = sanitize_text(data['task'], max_length=200)
            if not task:
                return jsonify({'message': 'Task cannot be empty'}), 400
            timesheet.task = task
        
        if 'productive_hours' in data:
            timesheet.productive_hours = float(data['productive_hours'])
        
        if 'non_productive_hours' in data:
            timesheet.non_productive_hours = float(data['non_productive_hours'])
        
        if 'description' in data:
            timesheet.description = sanitize_text(data['description'], max_length=500)
        
        # Validate hours after update
        is_valid, message = validate_hours(timesheet.productive_hours, timesheet.non_productive_hours)
        if not is_valid:
            return jsonify({'message': message}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': 'Timesheet updated successfully',
            'timesheet': timesheet.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'message': 'Invalid number format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@timesheet_bp.route('/timesheets/<int:id>', methods=['DELETE'])
@token_required
@block_demo_access
def delete_timesheet(current_user, id):
    """Delete timesheet entry"""
    try:
        timesheet = Timesheet.query.get(id)
        
        if not timesheet:
            return jsonify({'message': 'Timesheet not found'}), 404
        
        # Check ownership
        if timesheet.user_id != current_user.id and current_user.role not in ['admin', 'manager']:
            return jsonify({'message': 'Access denied'}), 403
        
        db.session.delete(timesheet)
        db.session.commit()
        
        return jsonify({'message': 'Timesheet deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
