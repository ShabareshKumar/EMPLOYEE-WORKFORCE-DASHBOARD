from flask_sqlalchemy import SQLAlchemy
import os
import logging

db = SQLAlchemy()
logger = logging.getLogger(__name__)

def init_db():
    """Initialize database and create tables"""
    from models.user import User
    from models.timesheet import Timesheet
    from models.project import Project, ProjectCategory, ProjectTask
    
    db.create_all()
    
    # Create demo user for placement/testing purposes
    demo_email = 'demo@demo.com'
    demo_user = User.query.filter_by(email=demo_email).first()
    
    if not demo_user:
        demo_user = User(
            name='Demo User',
            email=demo_email,
            role='employee',
            department='Demo Department',
            is_demo=True
        )
        demo_user.set_password('Demo123')
        db.session.add(demo_user)
        db.session.commit()
        logger.info(f"Demo user created: {demo_email}")
    
    # Check if any admin exists
    admin_exists = User.query.filter_by(role='admin', is_deleted=False).first()
    
    if not admin_exists:
        # Only create admin if environment variables are set
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')
        
        if admin_email and admin_password:
            admin = User(
                name=os.getenv('ADMIN_NAME', 'Admin User'),
                email=admin_email,
                role='admin',
                department='Management',
                is_demo=False
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            logger.info(f"Admin user created: {admin_email}")
        else:
            logger.warning("⚠️  No admin user exists. Set ADMIN_EMAIL and ADMIN_PASSWORD in environment variables to create one.")
            logger.warning("⚠️  Or use the CLI command: python create_admin.py")
