import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")
    # Continue without .env file

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password123@localhost:5432/sap_onboarding")

# Create SQLAlchemy engine with error handling
try:
    engine = create_engine(DATABASE_URL, echo=True)  # Enable SQL logging
    print(f"Database engine created successfully with URL: {DATABASE_URL}")
except Exception as e:
    print(f"Failed to create database engine: {e}")
    raise

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    try:
        print("Creating database tables...")
        # Import all models to register them with Base
        from models.user import User
        from db import UserState, ChatMessage
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        
        # Test database connection
        db = SessionLocal()
        try:
            # Test query to verify connection
            result = db.execute("SELECT 1").fetchone()
            print(f"Database connection test successful: {result}")
        except Exception as e:
            print(f"Database connection test failed: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"Failed to create database tables: {e}")
        raise

