from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import logging
import time
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Centralized settings import (loads .env & sets defaults)
from config import settings  # noqa: F401  # imported for side-effects

# Load environment variables (overrides still respected)
load_dotenv()

# Import our modules
from database import engine, Base, get_db, test_db_connection
from models import *  # Import all our new models
import schemas
from ai_service import ai_service

# Import all routers
from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.kpis import router as kpis_router
from routers.departments import router as departments_router
from routers.analytics import router as analytics_router
from routers.performance import router as performance_router
from routers.surveys import router as surveys_router
from routers.employees import router as employees_router
from routers.action_plans import router as action_plans_router
from routers.focus_groups import router as focus_groups_router
from routers.security import router as security_router
from routers import surveys, kpis, employees, departments, analytics, performance, parameters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# =====================================================
# MIDDLEWARE
# =====================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: Dict[str, Dict[str, Any]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        if client_ip not in self.clients:
            self.clients[client_ip] = {"calls": 1, "reset_time": current_time + self.period}
        else:
            client_data = self.clients[client_ip]
            if current_time > client_data["reset_time"]:
                client_data["calls"] = 1
                client_data["reset_time"] = current_time + self.period
            else:
                client_data["calls"] += 1

        if self.clients[client_ip]["calls"] > self.calls:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )

        response = await call_next(request)
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

# =====================================================
# FASTAPI APPLICATION
# =====================================================

app = FastAPI(
    title="HR Dashboard API",
    description="A comprehensive HR Dashboard API implementing the Golden Flow for employee engagement, KPI tracking, surveys, action plans, and efficacy measurement",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# =====================================================
# CORS CONFIGURATION
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting (more permissive for development)
if os.getenv("ENVIRONMENT", "development") == "production":
    app.add_middleware(RateLimitMiddleware, calls=1000, period=60)
else:
    app.add_middleware(RateLimitMiddleware, calls=10000, period=60)

# =====================================================
# ERROR HANDLERS
# =====================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "errors": [exc.detail] if isinstance(exc.detail, str) else exc.detail
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "errors": ["An unexpected error occurred"]
        }
    )

# =====================================================
# INCLUDE ROUTERS
# =====================================================

# Include all routers with API prefix
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(kpis_router, prefix="/api/v1")
app.include_router(departments_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(performance_router, prefix="/api/v1")
app.include_router(surveys_router, prefix="/api/v1")
app.include_router(employees_router, prefix="/api/v1")
app.include_router(action_plans_router, prefix="/api/v1")
app.include_router(focus_groups_router, prefix="/api/v1")
app.include_router(security_router, prefix="/api/v1")

# Add AI router
from routers.ai import router as ai_router
app.include_router(ai_router, prefix="/api")

# Include routers
app.include_router(surveys.router)
app.include_router(kpis.router)
app.include_router(employees.router)
app.include_router(departments.router)
app.include_router(analytics.router)
app.include_router(performance.router)
app.include_router(parameters.router)

# =====================================================
# STARTUP & SHUTDOWN EVENTS
# =====================================================

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("🚀 Starting HR Dashboard API...")
    
    # Initialize async database connection pool
    try:
        from services.database import init_database
        await init_database()
        logger.info("✅ Async database connection pool initialized")
    except Exception as e:
        logger.error(f"❌ Async database initialization failed: {e}")
        # Continue with fallback database for now
    
    # Test database connection
    if test_db_connection():
        logger.info("✅ Database connection established")
    else:
        logger.error("❌ Database connection failed")
        raise RuntimeError("Failed to connect to database")
    
    # Create tables (if they don't exist)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables verified/created")
    except Exception as e:
        logger.error(f"❌ Database table creation failed: {e}")
        raise RuntimeError("Failed to create database tables")
    
    # Initialize sample data for development
    if os.getenv("ENVIRONMENT", "development") == "development":
        await init_sample_data()
    
    logger.info("🎯 HR Dashboard API ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down HR Dashboard API...")
    
    # Close async database connection pool
    try:
        from services.database import close_database
        await close_database()
        logger.info("✅ Async database connection pool closed")
    except Exception as e:
        logger.error(f"❌ Error closing database pool: {e}")

# =====================================================
# CORE ROUTES
# =====================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HR Dashboard API",
        "version": "2.0.0",
        "status": "running",
        "documentation": "/docs",
        "golden_flow": {
            "step_1": "Set KPIs from dropdown/custom requirements",
            "step_2": "Conduct surveys/assessments to measure KPIs",
            "step_3": "Display results in visually appealing analytics",
            "step_4": "Recommend AI-driven Action Plans",
            "step_5": "Measure efficacy of Action Plans",
            "step_6": "Show honest results and recommendations",
            "step_7": "Continuous improvement loop"
        }
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Test AI service (basic check)
    try:
        ai_status = "healthy" if ai_service else "unavailable"
    except Exception as e:
        logger.error(f"AI service check failed: {e}")
        ai_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "ai_service": ai_status,
        "version": "2.0.0",
        "timestamp": time.time()
    }

@app.get("/api/system/info")
async def get_system_info():
    """Get system information"""
    return {
        "success": True,
        "message": "System information retrieved successfully",
        "data": {
            "name": "HR Dashboard API",
            "version": "2.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "database": "Supabase PostgreSQL",
            "features": {
                "authentication": True,
                "role_based_access": True,
                "kpi_management": True,
                "survey_system": True,
                "analytics": True,
                "ai_recommendations": True,
                "action_plans": True,
                "efficacy_measurement": True,
                "performance_management": True,
                "platform_integrations": True
            },
            "golden_flow_implemented": True
        }
    }

@app.get("/api/system/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    try:
        stats = {
            "users": db.query(User).count(),
            "active_users": db.query(User).filter(User.is_active == True).count(),
            "employees": db.query(Employee).count(),
            "departments": db.query(Department).count(),
            "kpis": db.query(KPI).count(),
            "active_kpis": db.query(KPI).filter(KPI.is_active == True).count(),
            "surveys": db.query(Survey).count(),
            "survey_responses": db.query(SurveyResponse).count(),
            "action_plans": db.query(ActionPlan).count(),
            "focus_groups": db.query(FocusGroup).count(),
        }
        
        return {
            "success": True,
            "message": "System statistics retrieved successfully",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve system statistics"
        )

# =====================================================
# SAMPLE DATA INITIALIZATION
# =====================================================

async def init_sample_data():
    """Initialize sample data for development"""
    try:
        from database import SessionLocal
        db = SessionLocal()
        
        # Check if data already exists
        if db.query(User).count() > 0:
            logger.info("Sample data already exists, skipping initialization")
            db.close()
            return
        
        logger.info("Initializing sample data...")
        
        # Create sample KPI categories
        categories = [
            KPICategory(name="Employee Engagement", description="Metrics related to employee satisfaction and engagement", color="#3B82F6"),
            KPICategory(name="Performance", description="Performance-related metrics", color="#10B981"),
            KPICategory(name="Retention", description="Employee retention and turnover metrics", color="#F59E0B"),
            KPICategory(name="Development", description="Learning and development metrics", color="#8B5CF6"),
            KPICategory(name="Well-being", description="Employee well-being and health metrics", color="#EF4444")
        ]
        
        for category in categories:
            db.add(category)
        
        db.commit()
        
        # Create sample departments
        departments = [
            Department(name="Engineering", description="Software development and technical teams"),
            Department(name="Human Resources", description="HR and people operations"),
            Department(name="Sales", description="Sales and business development"),
            Department(name="Marketing", description="Marketing and communications"),
            Department(name="Finance", description="Finance and accounting")
        ]
        
        for dept in departments:
            db.add(dept)
        
        db.commit()
        
        # Create admin user
        from auth import get_password_hash
        admin_user = User(
            email="admin@company.com",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        
        logger.info("Sample data initialized successfully")
        db.close()
        
    except Exception as e:
        logger.error(f"Failed to initialize sample data: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENVIRONMENT", "development") == "development" else False,
        log_level="info"
    ) 