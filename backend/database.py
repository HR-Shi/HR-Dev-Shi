from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase database configuration
SUPABASE_DATABASE_URL = os.getenv(
    "SUPABASE_DATABASE_URL",
    os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/hr_dashboard")
)

# Additional Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def create_database_engine():
    """Create database engine with multiple connection strategies"""
    
    # Try different connection configurations
    connection_configs = [
        # Standard connection
        {
            "url": SUPABASE_DATABASE_URL,
            "connect_args": {"connect_timeout": 30}
        },
        # Force IPv4 connection
        {
            "url": SUPABASE_DATABASE_URL + "?sslmode=require",
            "connect_args": {"connect_timeout": 30}
        },
        # Try with SSL disabled (for testing)
        {
            "url": SUPABASE_DATABASE_URL + "?sslmode=disable",
            "connect_args": {"connect_timeout": 30}
        },
        # Try with prefer SSL
        {
            "url": SUPABASE_DATABASE_URL + "?sslmode=prefer",
            "connect_args": {"connect_timeout": 30}
        }
    ]
    
    for i, config in enumerate(connection_configs, 1):
        try:
            logger.info(f"Attempting database connection strategy {i}/{len(connection_configs)}")
            
            engine = create_engine(
                config["url"],
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=os.getenv("SQL_DEBUG", "false").lower() == "true",
                connect_args=config["connect_args"]
            )
            
            # Test the connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info(f"✅ Database connection successful with strategy {i}")
                return engine
                
        except Exception as e:
            logger.warning(f"❌ Database connection strategy {i} failed: {e}")
            if i == len(connection_configs):
                logger.error("❌ All database connection strategies failed")
                raise
    
    return None

# Create engine with retry logic
try:
    engine = create_database_engine()
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    # Create a dummy engine for development that will fail gracefully
    engine = create_engine("sqlite:///./fallback.db")
    logger.warning("⚠️ Using fallback SQLite database due to connection issues")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test database connection with retry logic
def test_db_connection(max_retries=3, retry_delay=5):
    """Test database connection with retry logic"""
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            result = db.execute(text("SELECT 1")).fetchone()
            db.close()
            logger.info(f"✅ Database connection test successful: {result}")
            return True
        except Exception as e:
            logger.warning(f"❌ Database connection test failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("❌ All database connection test attempts failed")
                return False
    return False

# Check if we're using Supabase or fallback
def is_using_supabase():
    """Check if we're successfully connected to Supabase"""
    return "supabase.co" in str(engine.url)

# Get database info
def get_database_info():
    """Get information about the current database connection"""
    return {
        "engine_url": str(engine.url).replace(engine.url.password or "", "***") if engine.url.password else str(engine.url),
        "is_supabase": is_using_supabase(),
        "pool_size": engine.pool.size() if hasattr(engine.pool, 'size') else 'N/A',
        "dialect": engine.dialect.name
    } 