from flask import Blueprint, request, jsonify
from models.database import db
from models.project import Project, ProjectCategory, ProjectTask
from utils.auth import token_required, role_required
from utils.local_ai_analyzer import analyze_excel_file_private
from utils.validators import sanitize_text, validate_file_size, validate_file_extension
from utils.demo_middleware import block_demo_access
from werkzeug.utils import secure_filename
import io
import logging

project_bp = Blueprint('project', __name__)
logger = logging.getLogger(__name__)

# Maximum file size: 10MB
MAX_FILE_SIZE_MB = 10

@project_bp.route('/projects', methods=['GET'])
@token_required
def get_projects(current_user):
    """Get all projects"""
    try:
        projects = Project.query.filter_by(is_active=True).all()
        return jsonify({
            'projects': [p.to_dict() for p in projects]
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@project_bp.route('/projects/<int:id>', methods=['GET'])
@token_required
def get_project(current_user, id):
    """Get project with all categories and tasks"""
    try:
        project = Project.query.get(id)
        if not project:
            return jsonify({'message': 'Project not found'}), 404
        
        return jsonify({'project': project.to_dict()}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@project_bp.route('/projects', methods=['POST'])
@token_required
@role_required('admin', 'manager')
@block_demo_access
def create_project(current_user):
    """Create new project manually"""
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'message': 'Project name is required'}), 400
        
        # Check if project exists
        if Project.query.filter_by(name=data['name']).first():
            return jsonify({'message': 'Project with this name already exists'}), 400
        
        # Create project
        project = Project(
            name=sanitize_text(data['name'], max_length=200),
            description=sanitize_text(data.get('description', ''), max_length=500),
            created_by=current_user.id
        )
        
        db.session.add(project)
        db.session.flush()  # Get project ID
        
        # Add categories and tasks
        if data.get('categories'):
            for cat_order, cat_data in enumerate(data['categories']):
                category = ProjectCategory(
                    project_id=project.id,
                    name=sanitize_text(cat_data['name'], max_length=100),
                    order=cat_order
                )
                db.session.add(category)
                db.session.flush()  # Get category ID
                
                # Add tasks for this category
                if cat_data.get('tasks'):
                    for task_order, task_data in enumerate(cat_data['tasks']):
                        # Handle both string and dict formats
                        task_name = task_data if isinstance(task_data, str) else task_data.get('name', '')
                        task = ProjectTask(
                            category_id=category.id,
                            name=sanitize_text(task_name, max_length=200),
                            order=task_order
                        )
                        db.session.add(task)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Project created successfully',
            'project': project.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@project_bp.route('/projects/analyze', methods=['POST'])
@token_required
@role_required('admin', 'manager')
def analyze_project_file(current_user):
    """
    Analyze Excel file without creating project - PRIVACY-FOCUSED
    All processing done locally, no external API calls
    """
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'No file provided'}), 400
        
        file = request.files['file']
        privacy_mode = request.form.get('privacy_mode', 'strict')  # strict, normal, detailed
        
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
        
        # SECURITY: Sanitize filename to prevent path traversal attacks
        safe_filename = secure_filename(file.filename)
        if not safe_filename:
            return jsonify({'message': 'Invalid filename'}), 400
        
        # Validate file extension
        is_valid_ext, ext_message = validate_file_extension(
            safe_filename, 
            ['.xlsx', '.xls', '.csv']
        )
        if not is_valid_ext:
            return jsonify({'message': ext_message}), 400
        
        # Read file to check size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        # Validate file size (10MB max)
        is_valid_size, size_message = validate_file_size(file_size, MAX_FILE_SIZE_MB)
        if not is_valid_size:
            return jsonify({'message': size_message}), 400
        
        # Get file extension
        file_extension = '.' + safe_filename.rsplit('.', 1)[1].lower()
        
        # Read file content
        file_content = io.BytesIO(file.read())
        
        # Analyze with LOCAL AI (100% private)
        structured_data, analysis_summary, audit_log = analyze_excel_file_private(
            file_content, file_extension, privacy_mode
        )
        
        if not structured_data:
            return jsonify({
                'message': 'Could not analyze file',
                'analysis': analysis_summary,
                'privacy_assured': True
            }), 400
        
        logger.info(f"File analyzed by user {current_user.email}: {safe_filename}")
        
        # Return preview data
        return jsonify({
            'message': 'File analyzed successfully with local AI',
            'preview': structured_data,
            'analysis': analysis_summary,
            'stats': {
                'categories': len(structured_data.get('categories', [])),
                'total_tasks': sum(len(cat['tasks']) for cat in structured_data.get('categories', []))
            },
            'privacy': {
                'processing': 'local',
                'external_api_calls': 0,
                'data_transmitted': False,
                'audit_entries': len(audit_log)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"File analysis error: {str(e)}")
        return jsonify({'message': 'An error occurred while analyzing the file'}), 500

@project_bp.route('/projects/upload', methods=['POST'])
@token_required
@role_required('admin', 'manager')
@block_demo_access
def upload_project_excel(current_user):
    """
    Upload Excel file to create project structure with LOCAL AI analysis
    100% Privacy-Focused - No external API calls
    """
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'No file provided'}), 400
        
        file = request.files['file']
        project_name = request.form.get('project_name')
        project_description = request.form.get('project_description', '')
        privacy_mode = request.form.get('privacy_mode', 'strict')
        
        if not project_name:
            return jsonify({'message': 'Project name is required'}), 400
        
        # Sanitize project name and description
        project_name = sanitize_text(project_name, max_length=200)
        project_description = sanitize_text(project_description, max_length=500)
        
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
        
        # SECURITY: Sanitize filename to prevent path traversal attacks
        safe_filename = secure_filename(file.filename)
        if not safe_filename:
            return jsonify({'message': 'Invalid filename'}), 400
        
        # Validate file extension
        is_valid_ext, ext_message = validate_file_extension(
            safe_filename, 
            ['.xlsx', '.xls', '.csv']
        )
        if not is_valid_ext:
            return jsonify({'message': ext_message}), 400
        
        # Read file to check size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        # Validate file size (10MB max)
        is_valid_size, size_message = validate_file_size(file_size, MAX_FILE_SIZE_MB)
        if not is_valid_size:
            return jsonify({'message': size_message}), 400
        
        # Check if project exists
        if Project.query.filter_by(name=project_name).first():
            return jsonify({'message': 'Project with this name already exists'}), 400
        
        # Get file extension
        file_extension = '.' + safe_filename.rsplit('.', 1)[1].lower()
        
        # Read file content
        file_content = io.BytesIO(file.read())
        
        # Use LOCAL AI analyzer (100% private, no external calls)
        structured_data, analysis_summary, audit_log = analyze_excel_file_private(
            file_content, file_extension, privacy_mode
        )
        
        if not structured_data or not structured_data.get('categories'):
            return jsonify({
                'message': 'Could not extract valid data from file',
                'analysis': analysis_summary,
                'privacy_assured': True
            }), 400
        
        # Create project
        project = Project(
            name=sanitize_text(project_name, max_length=200),
            description=sanitize_text(project_description, max_length=500),
            created_by=current_user.id
        )
        
        db.session.add(project)
        db.session.flush()
        
        # Create categories and tasks from analyzed data
        categories_created = 0
        tasks_created = 0
        
        for cat_data in structured_data['categories']:
            # Create category
            category = ProjectCategory(
                project_id=project.id,
                name=sanitize_text(cat_data['name'], max_length=100),
                order=cat_data['order']
            )
            db.session.add(category)
            db.session.flush()
            categories_created += 1
            
            # Add tasks
            for task_data in cat_data['tasks']:
                task = ProjectTask(
                    category_id=category.id,
                    name=sanitize_text(task_data['name'], max_length=200),
                    order=task_data['order']
                )
                db.session.add(task)
                tasks_created += 1
        
        db.session.commit()
        
        logger.info(f"Project created by {current_user.email}: {project.name} ({categories_created} categories, {tasks_created} tasks)")
        
        return jsonify({
            'message': 'Project created successfully with local AI analysis',
            'project': project.to_dict(),
            'stats': {
                'categories': categories_created,
                'tasks': tasks_created
            },
            'analysis': analysis_summary,
            'privacy': {
                'processing': 'local',
                'external_api_calls': 0,
                'data_transmitted': False,
                'audit_entries': len(audit_log),
                'privacy_mode': privacy_mode
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Project upload error: {str(e)}")
        return jsonify({'message': 'An error occurred while uploading the project'}), 500

@project_bp.route('/projects/<int:id>', methods=['PUT'])
@token_required
@role_required('admin', 'manager')
def update_project(current_user, id):
    """Update project"""
    try:
        project = Project.query.get(id)
        if not project:
            return jsonify({'message': 'Project not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            # Check if new name conflicts
            existing = Project.query.filter(
                Project.name == data['name'],
                Project.id != id
            ).first()
            if existing:
                return jsonify({'message': 'Project with this name already exists'}), 400
            project.name = sanitize_text(data['name'], max_length=200)
        
        if 'description' in data:
            project.description = sanitize_text(data['description'], max_length=500)
        
        if 'is_active' in data:
            project.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': project.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@project_bp.route('/projects/<int:id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_project(current_user, id):
    """Delete project (admin only)"""
    try:
        project = Project.query.get(id)
        if not project:
            return jsonify({'message': 'Project not found'}), 404
        
        # Soft delete
        project.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Project deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@project_bp.route('/projects/<int:project_id>/categories/<int:category_id>/tasks', methods=['POST'])
@token_required
@role_required('admin', 'manager')
def add_task_to_category(current_user, project_id, category_id):
    """Add new task to a category"""
    try:
        category = ProjectCategory.query.filter_by(
            id=category_id,
            project_id=project_id
        ).first()
        
        if not category:
            return jsonify({'message': 'Category not found'}), 404
        
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'message': 'Task name is required'}), 400
        
        # Get max order
        max_order = db.session.query(db.func.max(ProjectTask.order)).filter_by(
            category_id=category_id
        ).scalar() or 0
        
        task = ProjectTask(
            category_id=category_id,
            name=sanitize_text(data['name'], max_length=200),
            description=sanitize_text(data.get('description', ''), max_length=500),
            order=max_order + 1
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'message': 'Task added successfully',
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
