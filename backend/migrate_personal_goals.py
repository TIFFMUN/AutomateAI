#!/usr/bin/env python3
"""
Database migration script to add personal_goals column to user_states table
"""
import os
import sys
from sqlalchemy import create_engine, text
from config import settings

def migrate_personal_goals():
    """Add personal_goals column to user_states table if it doesn't exist"""
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if personal_goals column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user_states' 
                AND column_name = 'personal_goals'
            """))
            
            if result.fetchone() is None:
                print("Adding personal_goals column to user_states table...")
                
                # Add the personal_goals column
                conn.execute(text("""
                    ALTER TABLE user_states 
                    ADD COLUMN personal_goals JSON DEFAULT '{"goals": [{"id": 1, "name": "Training", "progress": 0, "target": 100}, {"id": 2, "name": "Onboarding", "progress": 0, "target": 100}]}'
                """))
                
                # Update existing rows to have default personal_goals
                conn.execute(text("""
                    UPDATE user_states 
                    SET personal_goals = '{"goals": [{"id": 1, "name": "Training", "progress": 0, "target": 100}, {"id": 2, "name": "Onboarding", "progress": 0, "target": 100}]}'
                    WHERE personal_goals IS NULL
                """))
                
                conn.commit()
                print("✅ Successfully added personal_goals column!")
            else:
                print("✅ personal_goals column already exists!")
                
    except Exception as e:
        print(f"❌ Error migrating database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_personal_goals()
