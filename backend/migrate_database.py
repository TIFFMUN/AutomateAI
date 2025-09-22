#!/usr/bin/env python3
"""
Database migration script to add missing columns to existing tables.
This script handles the case where the database schema is out of sync with the models.
"""

import sys
import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError
from config import settings

def check_and_add_column(engine, table_name, column_name, column_definition):
    """Check if column exists and add it if it doesn't"""
    inspector = inspect(engine)
    
    # Get existing columns
    existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
    
    if column_name not in existing_columns:
        print(f"Adding missing column '{column_name}' to table '{table_name}'...")
        try:
            with engine.connect() as conn:
                # Use ALTER TABLE to add the column
                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
                conn.execute(text(alter_sql))
                conn.commit()
                print(f"✅ Successfully added column '{column_name}' to '{table_name}'")
                return True
        except Exception as e:
            print(f"❌ Failed to add column '{column_name}' to '{table_name}': {e}")
            return False
    else:
        print(f"✅ Column '{column_name}' already exists in table '{table_name}'")
        return True

def migrate_database():
    """Run database migration"""
    print("🔄 Starting database migration...")
    
    try:
        # Connect to the main database
        engine = create_engine(settings.DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Connected to main database successfully")
        
        # Check if user_states table exists
        inspector = inspect(engine)
        if 'user_states' not in inspector.get_table_names():
            print("❌ Table 'user_states' does not exist. Please run create_tables() first.")
            return False
        
        # Add missing personal_goals column
        success = check_and_add_column(
            engine, 
            'user_states', 
            'personal_goals', 
            'JSON DEFAULT \'{"goals": [{"id": 1, "name": "Training", "progress": 0, "target": 100}, {"id": 2, "name": "Onboarding", "progress": 0, "target": 100}]}\''
        )
        
        if success:
            print("✅ Database migration completed successfully!")
            return True
        else:
            print("❌ Database migration failed!")
            return False
            
    except Exception as e:
        print(f"❌ Database migration failed with error: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
