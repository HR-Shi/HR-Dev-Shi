"""
Database service module for async database connections
Provides get_db_connection dependency for FastAPI routers
"""

import asyncpg
import logging
from typing import Optional
import urllib.parse as urlparse

# Centralized settings
from config import settings

# Configure logging
logger = logging.getLogger(__name__)

class AsyncDatabaseConnection:
    """Async database connection wrapper"""
    
    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection
    
    async def fetch(self, query: str, *args):
        """Execute query and fetch all results"""
        return await self.connection.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Execute query and fetch one row"""
        return await self.connection.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Execute query and fetch single value"""
        return await self.connection.fetchval(query, *args)
    
    async def execute(self, query: str, *args):
        """Execute query without fetching results"""
        return await self.connection.execute(query, *args)
    
    async def executemany(self, query: str, args_list):
        """Execute query multiple times with different parameters"""
        return await self.connection.executemany(query, args_list)

class DatabaseService:
    """Database service for managing connections"""
    
    def __init__(self):
        self.db_url = self._get_database_url()
        self._pool: Optional[asyncpg.Pool] = None
    
    def _get_database_url(self) -> str:
        """Get database URL from environment variables"""
        # Try different environment variable names
        db_url = (
            settings.DATABASE_URL or 
            settings.SUPABASE_DATABASE_URL or
            "postgresql://postgres:password@localhost:5432/hr_dashboard"
        )
        
        # Ensure SSL mode for Supabase
        if 'supabase.com' in db_url and '?' not in db_url:
            db_url += '?sslmode=require'
        elif 'supabase.com' in db_url and 'sslmode=' not in db_url:
            db_url += '&sslmode=require'
        
        return db_url
    
    async def create_pool(self):
        """Create connection pool"""
        if self._pool is None:
            try:
                # Try direct connection first
                self._pool = await asyncpg.create_pool(
                    self.db_url,
                    min_size=2,
                    max_size=10,
                    server_settings={
                        'application_name': 'hr_dashboard_api'
                    }
                )
                logger.info("✅ AsyncPG connection pool created successfully")
            except Exception as e:
                logger.error(f"❌ Failed to create AsyncPG pool: {e}")
                # Try alternative connection method
                try:
                    parsed = urlparse.urlparse(self.db_url)
                    self._pool = await asyncpg.create_pool(
                        host=parsed.hostname,
                        port=parsed.port or 5432,
                        user=parsed.username,
                        password=parsed.password,
                        database=parsed.path.lstrip('/'),
                        ssl='require' if 'supabase.com' in self.db_url else None,
                        min_size=2,
                        max_size=10,
                        server_settings={
                            'application_name': 'hr_dashboard_api'
                        }
                    )
                    logger.info("✅ AsyncPG connection pool created using alternative method")
                except Exception as e2:
                    logger.error(f"❌ Failed to create AsyncPG pool with alternative method: {e2}")
                    raise e2
        
        return self._pool
    
    async def get_connection(self) -> AsyncDatabaseConnection:
        """Get a database connection from the pool"""
        if self._pool is None:
            await self.create_pool()
        
        connection = await self._pool.acquire()
        return AsyncDatabaseConnection(connection)
    
    async def release_connection(self, db_connection: AsyncDatabaseConnection):
        """Release a database connection back to the pool"""
        if self._pool and db_connection.connection:
            await self._pool.release(db_connection.connection)
    
    async def close_pool(self):
        """Close the connection pool"""
        if self._pool:
            await self._pool.close()
            self._pool = None

# Global database service instance
db_service = DatabaseService()

async def get_db_connection() -> AsyncDatabaseConnection:
    """
    FastAPI dependency for getting database connection
    This is what the parameters router imports and uses
    """
    connection = None
    try:
        connection = await db_service.get_connection()
        yield connection
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if connection:
            await db_service.release_connection(connection)

# Initialization and cleanup functions
async def init_database():
    """Initialize database connection pool"""
    try:
        await db_service.create_pool()
        logger.info("✅ Database service initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize database service: {e}")
        return False

async def close_database():
    """Close database connection pool"""
    await db_service.close_pool()
    logger.info("✅ Database service closed")

# Health check function
async def check_database_health() -> dict:
    """Check database health status"""
    try:
        connection = await db_service.get_connection()
        result = await connection.fetchval("SELECT 1")
        await db_service.release_connection(connection)
        
        return {
            "status": "healthy",
            "message": "Database connection successful",
            "test_result": result
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
            "test_result": None
        } 