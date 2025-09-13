import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Main PostgreSQL Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password123@localhost:5432/sap_onboarding")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB = os.getenv("POSTGRES_DB", "sap_onboarding")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password123")
    
    # Performance Testing Database
    PERFORMANCE_DATABASE_URL = os.getenv("PERFORMANCE_DATABASE_URL", "postgresql://postgres:password123@localhost:5433/performance_testing")
    PERFORMANCE_POSTGRES_HOST = os.getenv("PERFORMANCE_POSTGRES_HOST", "localhost")
    PERFORMANCE_POSTGRES_PORT = int(os.getenv("PERFORMANCE_POSTGRES_PORT", "5433"))
    PERFORMANCE_POSTGRES_DB = os.getenv("PERFORMANCE_POSTGRES_DB", "performance_testing")
    PERFORMANCE_POSTGRES_USER = os.getenv("PERFORMANCE_POSTGRES_USER", "postgres")
    PERFORMANCE_POSTGRES_PASSWORD = os.getenv("PERFORMANCE_POSTGRES_PASSWORD", "password123")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    PERFORMANCE_OPENAI_MODEL = os.getenv("PERFORMANCE_OPENAI_MODEL", "gpt-4")
    
    # Gemini Configuration (fallback)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # Application
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    PERFORMANCE_DEBUG = os.getenv("PERFORMANCE_DEBUG", "True").lower() == "true"
    PERFORMANCE_LOG_LEVEL = os.getenv("PERFORMANCE_LOG_LEVEL", "INFO")
    
    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
    PERFORMANCE_ALLOWED_ORIGINS = os.getenv("PERFORMANCE_ALLOWED_ORIGINS", "http://localhost:3002,http://localhost:3001").split(",")
    
settings = Settings()