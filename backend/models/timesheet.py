from models.database import db
from datetime import datetime, timezone

class Timesheet(db.Model):
    __tablename__ = 'timesheets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    
    # Legacy fields (for backward compatibility)
    project = db.Column(db.String(100), nullable=True)
    task = db.Column(db.String(200), nullable=True)
    
    # New structured fields
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('project_categories.id'), nullable=True, index=True)
    task_id = db.Column(db.Integer, db.ForeignKey('project_tasks.id'), nullable=True, index=True)
    
    productive_hours = db.Column(db.Float, nullable=False, default=0)
    non_productive_hours = db.Column(db.Float, nullable=False, default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    category_ref = db.relationship('ProjectCategory', foreign_keys=[category_id], backref='timesheet_entries')
    task_ref = db.relationship('ProjectTask', foreign_keys=[task_id], backref='timesheet_entries')
    
    def total_hours(self):
        """Calculate total hours"""
        return self.productive_hours + self.non_productive_hours
    
    def productivity_score(self):
        """Calculate productivity score"""
        total = self.total_hours()
        if total == 0:
            return 0
        return round((self.productive_hours / total) * 100, 2)
    
    def to_dict(self):
        """Convert timesheet to dictionary"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'date': self.date.isoformat() if self.date else None,
            'productive_hours': self.productive_hours,
            'non_productive_hours': self.non_productive_hours,
            'total_hours': self.total_hours(),
            'productivity_score': self.productivity_score(),
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Add structured project data if available
        if self.project_id and self.project_ref:
            result['project_id'] = self.project_id
            result['project_name'] = self.project_ref.name
            result['category_id'] = self.category_id
            result['category_name'] = self.category_ref.name if self.category_ref else None
            result['task_id'] = self.task_id
            result['task_name'] = self.task_ref.name if self.task_ref else None
        else:
            # Legacy format
            result['project'] = self.project
            result['task'] = self.task
        
        return result
