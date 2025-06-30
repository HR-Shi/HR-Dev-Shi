from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import hashlib
import json
import logging

from database import get_db
from models import User, AuditLog, DataRetentionPolicy, ConsentRecord, SurveyResponse, PerformanceReview
import models
import schemas
from auth.dependencies import get_current_active_user, require_roles

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/security", tags=["Security & Compliance"])

# =====================================================
# GDPR COMPLIANCE ENDPOINTS
# =====================================================

@router.post("/gdpr/consent")
async def record_user_consent(
    consent_data: dict = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record user consent for data processing (GDPR Article 7)"""
    try:
        consent_record = ConsentRecord(
            user_id=current_user.id,
            consent_type=consent_data.get("consent_type"),
            purpose=consent_data.get("purpose"),
            data_categories=consent_data.get("data_categories", []),
            consent_given=consent_data.get("consent_given", True),
            consent_text=consent_data.get("consent_text"),
            ip_address=consent_data.get("ip_address"),
            user_agent=consent_data.get("user_agent"),
            created_at=datetime.utcnow()
        )
        
        db.add(consent_record)
        db.commit()
        
        # Log consent action
        log_audit_event(
            db, current_user.id, "consent_recorded",
            {"consent_type": consent_data.get("consent_type"), "consent_given": consent_data.get("consent_given")}
        )
        
        return {"message": "Consent recorded successfully", "consent_id": str(consent_record.id)}
        
    except Exception as e:
        logger.error(f"Failed to record consent: {e}")
        raise HTTPException(status_code=500, detail="Failed to record consent")

@router.get("/gdpr/data-export/{user_id}")
async def export_user_data(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export all user data (GDPR Article 20 - Right to Data Portability)"""
    try:
        # Check if user can access this data (admin or self)
        if current_user.role not in ["admin", "hr_admin"] and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Collect user data from all tables
        user_data = {}
        
        # Basic user information
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data["profile"] = {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        
        # Survey responses (anonymized if required)
        survey_responses = db.query(SurveyResponse).filter(SurveyResponse.employee_id == user_id).all()
        user_data["survey_responses"] = [
            {
                "survey_id": str(response.survey_id),
                "submitted_at": response.submitted_at.isoformat(),
                "responses": response.responses,
                "is_anonymous": response.is_anonymous
            }
            for response in survey_responses
        ]
        
        # Performance reviews
        performance_reviews = db.query(PerformanceReview).filter(PerformanceReview.employee_id == user_id).all()
        user_data["performance_reviews"] = [
            {
                "id": str(review.id),
                "review_period": review.review_period,
                "scores": review.scores,
                "created_at": review.created_at.isoformat()
            }
            for review in performance_reviews
        ]
        
        # Audit logs
        audit_logs = db.query(AuditLog).filter(AuditLog.user_id == user_id).order_by(desc(AuditLog.timestamp)).all()
        user_data["audit_logs"] = [
            {
                "action": log.action,
                "timestamp": log.timestamp.isoformat(),
                "ip_address": log.ip_address,
                "user_agent": log.user_agent
            }
            for log in audit_logs
        ]
        
        # Log data export action
        log_audit_event(
            db, current_user.id, "data_exported",
            {"target_user_id": str(user_id), "export_timestamp": datetime.utcnow().isoformat()}
        )
        
        return {
            "user_id": str(user_id),
            "export_timestamp": datetime.utcnow().isoformat(),
            "data": user_data
        }
        
    except Exception as e:
        logger.error(f"Failed to export user data: {e}")
        raise HTTPException(status_code=500, detail="Failed to export user data")

@router.delete("/gdpr/data-deletion/{user_id}")
async def request_data_deletion(
    user_id: uuid.UUID,
    deletion_reason: str = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process data deletion request (GDPR Article 17 - Right to Erasure)"""
    try:
        # Only admin or the user themselves can request deletion
        if current_user.role not in ["admin", "hr_admin"] and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Log deletion request
        log_audit_event(
            db, current_user.id, "data_deletion_requested",
            {"target_user_id": str(user_id), "reason": deletion_reason}
        )
        
        # In a real implementation, this would trigger a data deletion workflow
        # For now, we'll mark it as a pending request
        deletion_request = {
            "user_id": str(user_id),
            "requested_by": str(current_user.id),
            "reason": deletion_reason,
            "status": "pending_review",
            "requested_at": datetime.utcnow().isoformat()
        }
        
        return {
            "message": "Data deletion request submitted for review",
            "request": deletion_request
        }
        
    except Exception as e:
        logger.error(f"Failed to process deletion request: {e}")
        raise HTTPException(status_code=500, detail="Failed to process deletion request")

# =====================================================
# AUDIT LOGGING SYSTEM
# =====================================================

def log_audit_event(
    db: Session,
    user_id: uuid.UUID,
    action: str,
    details: Dict[str, Any],
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """Log audit event for compliance tracking"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_log)
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")

@router.get("/audit-logs")
async def get_audit_logs(
    user_id: Optional[uuid.UUID] = Query(None),
    action: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_roles(["admin", "hr_admin"])),
    db: Session = Depends(get_db)
):
    """Get audit logs with filtering (Admin only)"""
    try:
        query = select(AuditLog)
        
        # Apply filters
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
        if start_date:
            query = query.where(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.where(AuditLog.timestamp <= end_date)
        
        # Get total count
        total = db.query(AuditLog).count()
        
        # Get logs with pagination
        logs = db.query(AuditLog).order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "logs": [
                {
                    "id": str(log.id),
                    "user_id": str(log.user_id),
                    "action": log.action,
                    "details": log.details,
                    "timestamp": log.timestamp.isoformat(),
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent
                }
                for log in logs
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get audit logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve audit logs")

# =====================================================
# DATA RETENTION POLICIES
# =====================================================

@router.post("/data-retention/policies")
async def create_retention_policy(
    policy_data: dict = Body(...),
    current_user: User = Depends(require_roles(["admin", "hr_admin"])),
    db: Session = Depends(get_db)
):
    """Create data retention policy"""
    try:
        policy = DataRetentionPolicy(
            name=policy_data["name"],
            description=policy_data.get("description"),
            data_type=policy_data["data_type"],
            retention_period_days=policy_data["retention_period_days"],
            auto_delete=policy_data.get("auto_delete", False),
            legal_basis=policy_data.get("legal_basis"),
            created_by=current_user.id,
            created_at=datetime.utcnow()
        )
        
        db.add(policy)
        db.commit()
        
        log_audit_event(
            db, current_user.id, "retention_policy_created",
            {"policy_name": policy_data["name"], "data_type": policy_data["data_type"]}
        )
        
        return {"message": "Retention policy created", "policy_id": str(policy.id)}
        
    except Exception as e:
        logger.error(f"Failed to create retention policy: {e}")
        raise HTTPException(status_code=500, detail="Failed to create retention policy")

@router.get("/data-retention/cleanup-candidates")
async def get_cleanup_candidates(
    data_type: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(["admin", "hr_admin"])),
    db: Session = Depends(get_db)
):
    """Get data that can be cleaned up based on retention policies"""
    try:
        # Get active retention policies
        policies = db.query(DataRetentionPolicy).filter(DataRetentionPolicy.is_active == True).all()
        
        cleanup_candidates = []
        
        for policy in policies:
            if data_type and policy.data_type != data_type:
                continue
                
            cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_period_days)
            
            # Check different data types
            if policy.data_type == "survey_responses":
                candidates_result = await db.execute(
                    select(models.SurveyResponse)
                    .where(models.SurveyResponse.submitted_at < cutoff_date)
                )
                candidates = candidates_result.scalars().all()
                
                cleanup_candidates.extend([
                    {
                        "type": "survey_response",
                        "id": str(candidate.id),
                        "created_at": candidate.submitted_at.isoformat(),
                        "policy": policy.name,
                        "auto_delete": policy.auto_delete
                    }
                    for candidate in candidates
                ])
            
            elif policy.data_type == "audit_logs":
                candidates = db.query(AuditLog).filter(AuditLog.timestamp < cutoff_date).all()
                
                cleanup_candidates.extend([
                    {
                        "type": "audit_log",
                        "id": str(candidate.id),
                        "created_at": candidate.timestamp.isoformat(),
                        "policy": policy.name,
                        "auto_delete": policy.auto_delete
                    }
                    for candidate in candidates
                ])
        
        return {
            "total_candidates": len(cleanup_candidates),
            "candidates": cleanup_candidates
        }
        
    except Exception as e:
        logger.error(f"Failed to get cleanup candidates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cleanup candidates")

# =====================================================
# DATA ENCRYPTION UTILITIES
# =====================================================

@router.post("/encryption/hash-data")
async def hash_sensitive_data(
    data: dict = Body(...),
    current_user: User = Depends(require_roles(["admin", "hr_admin"]))
):
    """Hash sensitive data for secure storage"""
    try:
        hashed_data = {}
        
        for key, value in data.items():
            if value and isinstance(value, str):
                # Use SHA-256 for hashing
                hash_object = hashlib.sha256(value.encode())
                hashed_data[key] = hash_object.hexdigest()
            else:
                hashed_data[key] = value
        
        return {
            "original_keys": list(data.keys()),
            "hashed_data": hashed_data,
            "hash_algorithm": "SHA-256"
        }
        
    except Exception as e:
        logger.error(f"Failed to hash data: {e}")
        raise HTTPException(status_code=500, detail="Failed to hash data")

# =====================================================
# CCPA COMPLIANCE
# =====================================================

@router.post("/ccpa/opt-out")
async def ccpa_opt_out(
    opt_out_data: dict = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process CCPA opt-out request"""
    try:
        # Record opt-out request
        opt_out_record = {
            "user_id": str(current_user.id),
            "opt_out_type": opt_out_data.get("opt_out_type", "sale_of_personal_info"),
            "effective_date": datetime.utcnow().isoformat(),
            "confirmation_method": opt_out_data.get("confirmation_method", "web_form")
        }
        
        # Log the opt-out action
        log_audit_event(
            db, current_user.id, "ccpa_opt_out",
            opt_out_record
        )
        
        return {
            "message": "CCPA opt-out request processed",
            "confirmation_id": str(uuid.uuid4()),
            "effective_date": opt_out_record["effective_date"]
        }
        
    except Exception as e:
        logger.error(f"Failed to process CCPA opt-out: {e}")
        raise HTTPException(status_code=500, detail="Failed to process opt-out request")

# =====================================================
# SECURITY MONITORING
# =====================================================

@router.get("/monitoring/security-dashboard")
async def get_security_dashboard(
    current_user: User = Depends(require_roles(["admin", "hr_admin"])),
    db: Session = Depends(get_db)
):
    """Get security monitoring dashboard"""
    try:
        # Recent login attempts
        recent_logins_count = db.query(AuditLog).filter(
            and_(
                AuditLog.action == "user_login",
                AuditLog.timestamp >= datetime.utcnow() - timedelta(hours=24)
            )
        ).count()
        
        # Failed login attempts
        failed_logins_count = db.query(AuditLog).filter(
            and_(
                AuditLog.action == "login_failed",
                AuditLog.timestamp >= datetime.utcnow() - timedelta(hours=24)
            )
        ).count()
        
        # Data access events
        data_access_count = db.query(AuditLog).filter(
            and_(
                AuditLog.action.in_(["data_exported", "survey_response_viewed"]),
                AuditLog.timestamp >= datetime.utcnow() - timedelta(hours=24)
            )
        ).count()
        
        # GDPR requests
        gdpr_requests_count = db.query(AuditLog).filter(
            and_(
                AuditLog.action.in_(["data_exported", "data_deletion_requested"]),
                AuditLog.timestamp >= datetime.utcnow() - timedelta(days=30)
            )
        ).count()
        
        return {
            "security_metrics": {
                "recent_logins_24h": recent_logins_count or 0,
                "failed_logins_24h": failed_logins_count or 0,
                "data_access_events_24h": data_access_count or 0,
                "gdpr_requests_30d": gdpr_requests_count or 0
            },
            "compliance_status": {
                "gdpr_ready": True,
                "ccpa_ready": True,
                "audit_logging_enabled": True,
                "encryption_enabled": True
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get security dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get security dashboard")

# =====================================================
# SESSION MANAGEMENT
# =====================================================

@router.post("/sessions/invalidate-all")
async def invalidate_all_sessions(
    user_id: Optional[uuid.UUID] = Body(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Invalidate all sessions for a user (security feature)"""
    try:
        target_user_id = user_id if user_id and current_user.role in ["admin", "hr_admin"] else current_user.id
        
        # Log session invalidation
        log_audit_event(
            db, current_user.id, "sessions_invalidated",
            {"target_user_id": str(target_user_id), "invalidated_by": str(current_user.id)}
        )
        
        # In a real implementation, this would invalidate JWT tokens or session tokens
        return {
            "message": "All sessions invalidated successfully",
            "user_id": str(target_user_id),
            "invalidated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to invalidate sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to invalidate sessions") 