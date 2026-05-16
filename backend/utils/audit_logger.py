"""
Audit logging system for tracking all data modifications
"""
from datetime import datetime, timezone
from models.database import db
from sqlalchemy import Column, Integer, String, DateTime, Text
import json
import logging

logger = logging.getLogger(__name__)


class AuditLog(db.Model):
    """Audit log model for tracking all data modifications"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)  # Nullable for system actions
    user_email = Column(String(120), nullable=True)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    entity_type = Column(String(50), nullable=False)  # User, Timesheet, Project, etc.
    entity_id = Column(Integer, nullable=True)
    changes = Column(Text, nullable=True)  # JSON string of changes
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'changes': json.loads(self.changes) if self.changes else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat()
        }


def log_audit(user, action, entity_type, entity_id=None, changes=None, request=None):
    """
    Log an audit entry
    
    Args:
        user: User object or None for system actions
        action: Action performed (CREATE, UPDATE, DELETE, LOGIN, etc.)
        entity_type: Type of entity (User, Timesheet, Project, etc.)
        entity_id: ID of the entity (optional)
        changes: Dictionary of changes made (optional)
        request: Flask request object (optional)
    """
    try:
        audit_entry = AuditLog(
            user_id=user.id if user else None,
            user_email=user.email if user else 'system',
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=json.dumps(changes) if changes else None,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent', '')[:255] if request else None
        )
        
        db.session.add(audit_entry)
        db.session.commit()
        
        logger.info(f"Audit log: {action} {entity_type} by {user.email if user else 'system'}")
        
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")
        # Don't fail the main operation if audit logging fails
        db.session.rollback()


def get_audit_logs(entity_type=None, entity_id=None, user_id=None, limit=100):
    """
    Retrieve audit logs with optional filters
    
    Args:
        entity_type: Filter by entity type
        entity_id: Filter by entity ID
        user_id: Filter by user ID
        limit: Maximum number of records to return
    
    Returns:
        List of audit log dictionaries
    """
    query = AuditLog.query
    
    if entity_type:
        query = query.filter_by(entity_type=entity_type)
    
    if entity_id:
        query = query.filter_by(entity_id=entity_id)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    query = query.order_by(AuditLog.timestamp.desc()).limit(limit)
    
    return [log.to_dict() for log in query.all()]
