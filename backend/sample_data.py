#!/usr/bin/env python3
"""
Sample data script to populate the database with test users and feedback
Run this script to add sample data for testing the performance feedback system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import (
    SessionLocal, create_tables, User, PerformanceFeedback,
    create_user, create_performance_feedback
)

def create_sample_data():
    """Create sample users and performance feedback"""
    
    # Create database tables
    create_tables()
    
    db = SessionLocal()
    
    try:
        # Create sample users
        print("Creating sample users...")
        
        # Create a manager
        manager = create_user(
            db=db,
            user_id="manager001",
            name="Sarah Johnson",
            email="sarah.johnson@company.com",
            role="manager"
        )
        print(f"Created manager: {manager.name}")
        
        # Create employees
        employee1 = create_user(
            db=db,
            user_id="employee001",
            name="John Smith",
            email="john.smith@company.com",
            role="employee",
            manager_id=manager.id
        )
        print(f"Created employee: {employee1.name}")
        
        employee2 = create_user(
            db=db,
            user_id="employee002",
            name="Emily Davis",
            email="emily.davis@company.com",
            role="employee",
            manager_id=manager.id
        )
        print(f"Created employee: {employee2.name}")
        
        employee3 = create_user(
            db=db,
            user_id="employee003",
            name="Michael Brown",
            email="michael.brown@company.com",
            role="employee",
            manager_id=manager.id
        )
        print(f"Created employee: {employee3.name}")
        
        # Create sample performance feedback
        print("Creating sample performance feedback...")
        
        feedback1 = create_performance_feedback(
            db=db,
            employee_id=employee1.id,
            manager_id=manager.id,
            feedback_text="""John has shown excellent progress this quarter. His technical skills have improved significantly, and he's become more proactive in taking on challenging tasks. He consistently meets deadlines and produces high-quality work. 

Areas for improvement include communication during team meetings - he could be more vocal about his ideas and concerns. Also, he should work on delegating tasks more effectively when leading small projects.

Overall, John is a valuable team member who shows great potential for growth."""
        )
        print(f"Created feedback for {employee1.name}")
        
        feedback2 = create_performance_feedback(
            db=db,
            employee_id=employee2.id,
            manager_id=manager.id,
            feedback_text="""Emily has been outstanding this quarter. Her attention to detail is exceptional, and she consistently delivers work that exceeds expectations. She's also been a great mentor to junior team members.

Her communication skills are excellent, and she's always willing to help others. She takes initiative on process improvements and has suggested several valuable optimizations.

The only area for growth would be taking on more leadership responsibilities, as she has the skills and knowledge to lead larger projects."""
        )
        print(f"Created feedback for {employee2.name}")
        
        feedback3 = create_performance_feedback(
            db=db,
            employee_id=employee3.id,
            manager_id=manager.id,
            feedback_text="""Michael has made steady progress this quarter. He's reliable and always completes his assigned tasks on time. His technical knowledge is solid, and he's good at troubleshooting issues.

However, there are some areas that need attention. He sometimes struggles with time management when working on multiple projects simultaneously. Also, his written communication could be clearer and more concise.

I'd like to see Michael take more initiative in proposing solutions and being more collaborative with team members."""
        )
        print(f"Created feedback for {employee3.name}")
        
        print("\nSample data created successfully!")
        print(f"Manager: {manager.name} (ID: {manager.user_id})")
        print(f"Employees:")
        print(f"  - {employee1.name} (ID: {employee1.user_id})")
        print(f"  - {employee2.name} (ID: {employee2.user_id})")
        print(f"  - {employee3.name} (ID: {employee3.user_id})")
        print(f"Created {3} performance feedback entries")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
