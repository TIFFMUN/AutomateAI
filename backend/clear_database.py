#!/usr/bin/env python3
"""
Script to clear all database entries and reset the database.
This will delete all data from all tables.
"""

import sys
import os
from sqlalchemy import create_engine, text
from config import settings

def clear_database():
    """Clear all data from the database"""
    print("🗑️  Clearing database...")
    
    try:
        # Connect to the main database
        engine = create_engine(settings.DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Connected to main database successfully")
        
        # Clear all tables in the correct order (respecting foreign key constraints)
        tables_to_clear = [
            "chat_messages",
            "user_states", 
            "users"
        ]
        
        with engine.connect() as conn:
            for table in tables_to_clear:
                try:
                    result = conn.execute(text(f"DELETE FROM {table}"))
                    deleted_count = result.rowcount
                    print(f"✅ Cleared {deleted_count} rows from {table}")
                except Exception as e:
                    print(f"⚠️  Could not clear {table}: {e}")
            
            conn.commit()
        
        # Clear performance database
        if hasattr(settings, 'PERFORMANCE_DATABASE_URL'):
            perf_engine = create_engine(settings.PERFORMANCE_DATABASE_URL)
            
            with perf_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Connected to performance database successfully")
            
            perf_tables_to_clear = [
                "performance_metrics",
                "performance_goals", 
                "performance_feedbacks",
                "progress_updates",
                "performance_users"
            ]
            
            with perf_engine.connect() as conn:
                for table in perf_tables_to_clear:
                    try:
                        result = conn.execute(text(f"DELETE FROM {table}"))
                        deleted_count = result.rowcount
                        print(f"✅ Cleared {deleted_count} rows from {table}")
                    except Exception as e:
                        print(f"⚠️  Could not clear {table}: {e}")
                
                conn.commit()
        
        print("✅ Database cleared successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False

if __name__ == "__main__":
    success = clear_database()
    sys.exit(0 if success else 1)
