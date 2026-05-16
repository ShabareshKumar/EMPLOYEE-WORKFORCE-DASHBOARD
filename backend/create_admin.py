#!/usr/bin/env python3
"""
CLI script to create an admin user
Usage: python create_admin.py
"""
import sys
import getpass
from app import create_app
from models.database import db
from models.user import User
from utils.validators import is_valid_email, validate_password

def create_admin():
    """Create admin user via CLI"""
    print("=" * 60)
    print("CREATE ADMIN USER")
    print("=" * 60)
    print()
    
    # Get user input
    name = input("Admin Name: ").strip()
    if not name:
        print("❌ Name is required")
        sys.exit(1)
    
    email = input("Admin Email: ").strip().lower()
    if not is_valid_email(email):
        print("❌ Invalid email format")
        sys.exit(1)
    
    password = getpass.getpass("Admin Password: ")
    password_confirm = getpass.getpass("Confirm Password: ")
    
    if password != password_confirm:
        print("❌ Passwords do not match")
        sys.exit(1)
    
    is_valid, message = validate_password(password)
    if not is_valid:
        print(f"❌ {message}")
        sys.exit(1)
    
    department = input("Department (optional): ").strip() or "Management"
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"❌ User with email {email} already exists")
            sys.exit(1)
        
        # Create admin user
        admin = User(
            name=name,
            email=email,
            role='admin',
            department=department,
            is_demo=False
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print()
        print("=" * 60)
        print("✅ ADMIN USER CREATED SUCCESSFULLY")
        print("=" * 60)
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Role: admin")
        print(f"Department: {department}")
        print()
        print("You can now login with these credentials.")
        print("=" * 60)

if __name__ == '__main__':
    try:
        create_admin()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
