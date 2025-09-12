#!/usr/bin/env python3
"""
Script to create performance users for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import get_performance_db, create_performance_user, PerformanceUser
from sqlalchemy.orm import Session

def create_test_users():
    """Create test users in the performance database"""
    
    # Get database session
    db_gen = get_performance_db()
    db = next(db_gen)
    
    try:
        # Check if users already exist
        existing_users = db.query(PerformanceUser).count()
        if existing_users > 0:
            print(f"Performance database already has {existing_users} users. Skipping creation.")
            return
        
        # Create manager (Alex Thompson)
        manager = create_performance_user(
            db=db,
            user_id="perf_manager001",
            name="Alex Thompson",
            email="alex.thompson@company.com",
            role="Manager"
        )
        print(f"Created manager: {manager.name} (ID: {manager.id})")
        
        # Create employees
        employees = [
            ("perf_employee001", "Sarah Chen", "sarah.chen@company.com", "Employee"),
            ("perf_employee002", "David Rodriguez", "david.rodriguez@company.com", "Employee"),
            ("perf_employee003", "Lisa Park", "lisa.park@company.com", "Employee")
        ]
        
        created_employees = []
        for user_id, name, email, role in employees:
            employee = create_performance_user(
                db=db,
                user_id=user_id,
                name=name,
                email=email,
                role=role,
                manager_id=manager.id  # Set Alex as their manager
            )
            created_employees.append(employee)
            print(f"Created employee: {employee.name} (ID: {employee.id})")
        
        print(f"\nSuccessfully created {len(created_employees) + 1} users:")
        print(f"- 1 Manager: Alex Thompson")
        print(f"- {len(created_employees)} Employees: {', '.join([emp.name for emp in created_employees])}")
        
    except Exception as e:
        print(f"Error creating users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()
