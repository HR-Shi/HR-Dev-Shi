from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from typing import List, Optional, Dict, Any
import models
import schemas
from database import get_db
from auth.dependencies import get_current_active_user, require_roles
import logging
from datetime import datetime, timedelta
import uuid
from decimal import Decimal
from ai_service import ai_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/performance",
    tags=["Performance Management"]
)

# =============================================================================
# CONTINUOUS FEEDBACK SYSTEM
# =============================================================================

@router.post("/feedback", response_model=schemas.Feedback)
async def create_feedback(
    feedback: schemas.FeedbackBase,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create continuous feedback entry"""
    try:
        # Validate that the recipient exists
        recipient = db.query(models.Employee).filter(models.Employee.id == feedback.recipient_id).first()
        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient employee not found"
            )
        
        # Create feedback entry
        db_feedback = models.Feedback(
            recipient_id=feedback.recipient_id,
            giver_id=current_user.employee_id,
            feedback_type=feedback.feedback_type,
            category=feedback.category,
            content=feedback.content,
            rating=feedback.rating,
            is_anonymous=feedback.is_anonymous,
            related_review_id=feedback.related_review_id,
            tags=feedback.tags
        )
        
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        logger.info(f"Feedback created by {current_user.email} for employee {feedback.recipient_id}")
        return db_feedback
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create feedback: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create feedback"
        )

@router.get("/feedback/{employee_id}")
async def get_employee_feedback(
    employee_id: uuid.UUID,
    feedback_type: Optional[str] = Query(None, enum=["peer", "upward", "downward", "self"]),
    category: Optional[str] = Query(None, enum=["performance", "behavior", "skills", "communication"]),
    limit: int = Query(50, ge=1, le=200),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get feedback for an employee"""
    try:
        # Check permissions
        can_view = False
        if current_user.role in ["admin", "hr_admin"]:
            can_view = True
        elif current_user.employee_id == employee_id:
            can_view = True
        elif current_user.role == "manager":
            # Check if this is their direct report
            employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
            if employee and current_user.employee_id:
                manager = db.query(models.Employee).filter(models.Employee.id == current_user.employee_id).first()
                if manager and employee.manager_id == manager.id:
                    can_view = True
        
        if not can_view:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this employee's feedback"
            )
        
        # Build query
        query = db.query(models.Feedback).filter(models.Feedback.recipient_id == employee_id)
        
        if feedback_type:
            query = query.filter(models.Feedback.feedback_type == feedback_type)
        if category:
            query = query.filter(models.Feedback.category == category)
        
        feedback_list = query.order_by(desc(models.Feedback.created_at)).limit(limit).all()
        
        # Calculate feedback analytics
        total_feedback = len(feedback_list)
        avg_rating = None
        if feedback_list:
            ratings = [f.rating for f in feedback_list if f.rating is not None]
            avg_rating = sum(ratings) / len(ratings) if ratings else None
        
        # Feedback breakdown by type
        type_breakdown = {"peer": 0, "upward": 0, "downward": 0, "self": 0}
        category_breakdown = {"performance": 0, "behavior": 0, "skills": 0, "communication": 0}
        
        for feedback in feedback_list:
            if feedback.feedback_type in type_breakdown:
                type_breakdown[feedback.feedback_type] += 1
            if feedback.category and feedback.category in category_breakdown:
                category_breakdown[feedback.category] += 1
        
        return {
            "employee_id": employee_id,
            "feedback": feedback_list,
            "analytics": {
                "total_feedback": total_feedback,
                "average_rating": round(avg_rating, 2) if avg_rating else None,
                "breakdown_by_type": type_breakdown,
                "breakdown_by_category": category_breakdown
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get feedback for employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employee feedback"
        )

@router.post("/feedback/request-360")
async def request_360_feedback(
    employee_id: uuid.UUID,
    feedback_request: Dict[str, Any],
    current_user: models.User = Depends(require_roles(["admin", "hr_admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Request 360-degree feedback for an employee"""
    try:
        employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Get feedback providers
        peer_ids = feedback_request.get("peer_ids", [])
        manager_ids = feedback_request.get("manager_ids", [])
        direct_report_ids = feedback_request.get("direct_report_ids", [])
        include_self = feedback_request.get("include_self", True)
        
        feedback_requests = []
        
        # Create peer feedback requests
        for peer_id in peer_ids:
            feedback_requests.append({
                "recipient_id": employee_id,
                "requested_from": peer_id,
                "feedback_type": "peer",
                "due_date": feedback_request.get("due_date"),
                "instructions": feedback_request.get("peer_instructions", "Please provide honest feedback on this colleague's performance.")
            })
        
        # Create manager feedback requests
        for manager_id in manager_ids:
            feedback_requests.append({
                "recipient_id": employee_id,
                "requested_from": manager_id,
                "feedback_type": "downward",
                "due_date": feedback_request.get("due_date"),
                "instructions": feedback_request.get("manager_instructions", "Please provide feedback as this employee's manager.")
            })
        
        # Create direct report feedback requests
        for report_id in direct_report_ids:
            feedback_requests.append({
                "recipient_id": employee_id,
                "requested_from": report_id,
                "feedback_type": "upward",
                "due_date": feedback_request.get("due_date"),
                "instructions": feedback_request.get("report_instructions", "Please provide feedback on your manager's leadership.")
            })
        
        # Self-assessment request
        if include_self:
            feedback_requests.append({
                "recipient_id": employee_id,
                "requested_from": employee_id,
                "feedback_type": "self",
                "due_date": feedback_request.get("due_date"),
                "instructions": feedback_request.get("self_instructions", "Please complete your self-assessment.")
            })
        
        # Store feedback requests (you might want to create a FeedbackRequest model)
        # For now, we'll return the request structure
        
        logger.info(f"360-degree feedback requested by {current_user.email} for employee {employee_id}")
        
        return {
            "message": f"360-degree feedback requested for {employee.name}",
            "employee_id": employee_id,
            "total_requests": len(feedback_requests),
            "feedback_requests": feedback_requests,
            "due_date": feedback_request.get("due_date"),
            "requested_by": current_user.email,
            "requested_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to request 360 feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request 360-degree feedback"
        )

# =============================================================================
# PERFORMANCE REVIEW CYCLES
# =============================================================================

@router.post("/review-cycles", response_model=schemas.PerformanceReviewCycle)
async def create_review_cycle(
    cycle: schemas.PerformanceReviewCycleCreate,
    current_user: models.User = Depends(require_roles(["admin", "hr_admin"])),
    db: Session = Depends(get_db)
):
    """Create a new performance review cycle"""
    try:
        db_cycle = models.PerformanceReviewCycle(
            name=cycle.name,
            description=cycle.description,
            type=cycle.type,
            start_date=cycle.start_date,
            end_date=cycle.end_date,
            status=cycle.status,
            departments=cycle.departments,
            template_config=cycle.template_config,
            created_by=current_user.id
        )
        
        db.add(db_cycle)
        db.commit()
        db.refresh(db_cycle)
        
        logger.info(f"Performance review cycle created by {current_user.email}: {cycle.name}")
        return db_cycle
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create review cycle: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create performance review cycle"
        )

@router.get("/review-cycles")
async def get_review_cycles(
    status: Optional[str] = Query(None, enum=["planning", "active", "review", "completed"]),
    type: Optional[str] = Query(None, enum=["annual", "quarterly", "monthly", "project_based"]),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get performance review cycles"""
    try:
        query = db.query(models.PerformanceReviewCycle)
        
        if status:
            query = query.filter(models.PerformanceReviewCycle.status == status)
        if type:
            query = query.filter(models.PerformanceReviewCycle.type == type)
        
        cycles = query.order_by(desc(models.PerformanceReviewCycle.start_date)).all()
        
        return {"cycles": cycles, "total": len(cycles)}
        
    except Exception as e:
        logger.error(f"Failed to get review cycles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve review cycles"
        )

@router.post("/reviews", response_model=schemas.PerformanceReview)
async def create_performance_review(
    review: schemas.PerformanceReviewCreate,
    current_user: models.User = Depends(require_roles(["admin", "hr_admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Create a performance review"""
    try:
        # Validate employee and reviewer exist
        employee = db.query(models.Employee).filter(models.Employee.id == review.employee_id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        reviewer = db.query(models.Employee).filter(models.Employee.id == review.reviewer_id).first()
        if not reviewer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reviewer not found"
            )
        
        db_review = models.PerformanceReview(
            employee_id=review.employee_id,
            reviewer_id=review.reviewer_id,
            cycle_id=review.cycle_id,
            rating=review.rating,
            comments=review.comments,
            status=review.status,
            self_assessment=review.self_assessment,
            peer_feedback=review.peer_feedback,
            manager_feedback=review.manager_feedback,
            goals_for_next_period=review.goals_for_next_period,
            calibration_score=review.calibration_score,
            review_type=review.review_type
        )
        
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        
        logger.info(f"Performance review created by {current_user.email} for employee {review.employee_id}")
        return db_review
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create performance review: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create performance review"
        )

@router.get("/reviews/{employee_id}")
async def get_employee_reviews(
    employee_id: uuid.UUID,
    cycle_id: Optional[uuid.UUID] = None,
    review_type: Optional[str] = Query(None, enum=["annual", "quarterly", "monthly", "project_based"]),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get performance reviews for an employee"""
    try:
        # Check permissions
        can_view = False
        if current_user.role in ["admin", "hr_admin"]:
            can_view = True
        elif current_user.employee_id == employee_id:
            can_view = True
        elif current_user.role == "manager":
            employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
            if employee and current_user.employee_id:
                manager = db.query(models.Employee).filter(models.Employee.id == current_user.employee_id).first()
                if manager and employee.manager_id == manager.id:
                    can_view = True
        
        if not can_view:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this employee's reviews"
            )
        
        query = db.query(models.PerformanceReview).filter(
            models.PerformanceReview.employee_id == employee_id
        )
        
        if cycle_id:
            query = query.filter(models.PerformanceReview.cycle_id == cycle_id)
        if review_type:
            query = query.filter(models.PerformanceReview.review_type == review_type)
        
        reviews = query.order_by(desc(models.PerformanceReview.created_at)).all()
        
        # Calculate review analytics
        avg_rating = None
        if reviews:
            ratings = [r.rating for r in reviews]
            avg_rating = sum(ratings) / len(ratings)
        
        # Rating trend
        rating_trend = "stable"
        if len(reviews) >= 2:
            recent_avg = sum([r.rating for r in reviews[:3]]) / min(3, len(reviews))
            older_avg = sum([r.rating for r in reviews[-3:]]) / min(3, len(reviews))
            if recent_avg > older_avg + 0.2:
                rating_trend = "improving"
            elif recent_avg < older_avg - 0.2:
                rating_trend = "declining"
        
        return {
            "employee_id": employee_id,
            "reviews": reviews,
            "analytics": {
                "total_reviews": len(reviews),
                "average_rating": round(avg_rating, 2) if avg_rating else None,
                "rating_trend": rating_trend,
                "latest_review_date": reviews[0].created_at if reviews else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get reviews for employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employee reviews"
        )

@router.post("/reviews/{review_id}/calibrate")
async def calibrate_review(
    review_id: uuid.UUID,
    calibration_data: Dict[str, Any],
    current_user: models.User = Depends(require_roles(["admin", "hr_admin"])),
    db: Session = Depends(get_db)
):
    """Calibrate performance review ratings for fairness"""
    try:
        review = db.query(models.PerformanceReview).filter(models.PerformanceReview.id == review_id).first()
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Performance review not found"
            )
        
        # Get calibration peer group (same department, similar role)
        employee = db.query(models.Employee).filter(models.Employee.id == review.employee_id).first()
        
        peer_reviews = db.query(models.PerformanceReview).join(
            models.Employee, models.PerformanceReview.employee_id == models.Employee.id
        ).filter(
            and_(
                models.Employee.department_id == employee.department_id,
                models.Employee.position == employee.position,
                models.PerformanceReview.review_type == review.review_type,
                models.PerformanceReview.id != review_id
            )
        ).all()
        
        if len(peer_reviews) < 3:
            return {
                "message": "Insufficient peer data for calibration",
                "peer_count": len(peer_reviews),
                "calibration_applied": False
            }
        
        # Calculate peer statistics
        peer_ratings = [r.rating for r in peer_reviews]
        peer_avg = sum(peer_ratings) / len(peer_ratings)
        peer_std = (sum([(r - peer_avg) ** 2 for r in peer_ratings]) / len(peer_ratings)) ** 0.5
        
        # Calculate calibrated score
        current_rating = review.rating
        z_score = (current_rating - peer_avg) / peer_std if peer_std > 0 else 0
        
        # Apply calibration logic
        calibrated_score = current_rating
        if abs(z_score) > 2:  # Outlier detection
            # Adjust toward peer mean
            adjustment_factor = calibration_data.get("adjustment_factor", 0.3)
            if z_score > 2:
                calibrated_score = current_rating - (adjustment_factor * (current_rating - peer_avg))
            else:
                calibrated_score = current_rating + (adjustment_factor * (peer_avg - current_rating))
        
        # Update review
        review.calibration_score = Decimal(str(round(calibrated_score, 2)))
        review.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Review calibrated by {current_user.email}: {review_id}")
        
        return {
            "review_id": review_id,
            "original_rating": current_rating,
            "calibrated_score": float(review.calibration_score),
            "peer_average": round(peer_avg, 2),
            "z_score": round(z_score, 2),
            "peer_count": len(peer_reviews),
            "calibration_applied": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calibrate review {review_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calibrate performance review"
        )

# =============================================================================
# 1:1 MEETING MANAGEMENT
# =============================================================================

@router.post("/meetings/schedule")
async def schedule_one_on_one(
    meeting_data: Dict[str, Any],
    current_user: models.User = Depends(require_roles(["admin", "hr_admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Schedule a 1:1 meeting"""
    try:
        employee_id = meeting_data.get("employee_id")
        manager_id = meeting_data.get("manager_id", current_user.employee_id)
        
        # Validate participants
        employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
        manager = db.query(models.Employee).filter(models.Employee.id == manager_id).first()
        
        if not employee or not manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee or manager not found"
            )
        
        # Create meeting record (you might want a Meeting model)
        meeting = {
            "id": str(uuid.uuid4()),
            "employee_id": employee_id,
            "manager_id": manager_id,
            "scheduled_date": meeting_data.get("scheduled_date"),
            "duration_minutes": meeting_data.get("duration_minutes", 60),
            "agenda_items": meeting_data.get("agenda_items", []),
            "location": meeting_data.get("location", "Virtual"),
            "status": "scheduled",
            "created_by": current_user.id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # In a real implementation, you'd save this to a Meeting table
        # For now, we'll return the meeting data
        
        logger.info(f"1:1 meeting scheduled by {current_user.email} between {employee.name} and {manager.name}")
        
        return {
            "message": "1:1 meeting scheduled successfully",
            "meeting": meeting
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to schedule 1:1 meeting: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule 1:1 meeting"
        )

@router.get("/meetings/{employee_id}")
async def get_employee_meetings(
    employee_id: uuid.UUID,
    status: Optional[str] = Query(None, enum=["scheduled", "completed", "cancelled"]),
    limit: int = Query(20, ge=1, le=100),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get 1:1 meetings for an employee"""
    try:
        # Check permissions
        can_view = False
        if current_user.role in ["admin", "hr_admin"]:
            can_view = True
        elif current_user.employee_id == employee_id:
            can_view = True
        elif current_user.role == "manager":
            employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
            if employee and current_user.employee_id:
                manager = db.query(models.Employee).filter(models.Employee.id == current_user.employee_id).first()
                if manager and employee.manager_id == manager.id:
                    can_view = True
        
        if not can_view:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this employee's meetings"
            )
        
        # For demo purposes, return mock meeting data
        # In a real implementation, you'd query from a Meeting table
        mock_meetings = [
            {
                "id": str(uuid.uuid4()),
                "employee_id": employee_id,
                "manager_id": str(uuid.uuid4()),
                "scheduled_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "duration_minutes": 60,
                "agenda_items": ["Career development", "Current projects", "Feedback"],
                "status": "scheduled",
                "action_items": [],
                "meeting_notes": ""
            },
            {
                "id": str(uuid.uuid4()),
                "employee_id": employee_id,
                "manager_id": str(uuid.uuid4()),
                "scheduled_date": (datetime.utcnow() - timedelta(days=14)).isoformat(),
                "duration_minutes": 45,
                "agenda_items": ["Performance review", "Goals setting"],
                "status": "completed",
                "action_items": ["Complete training module", "Submit project proposal"],
                "meeting_notes": "Great progress on current projects. Focus on skill development."
            }
        ]
        
        if status:
            mock_meetings = [m for m in mock_meetings if m["status"] == status]
        
        return {
            "employee_id": employee_id,
            "meetings": mock_meetings[:limit],
            "total": len(mock_meetings)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get meetings for employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employee meetings"
        )

# =============================================================================
# PERFORMANCE ANALYTICS
# =============================================================================

@router.get("/analytics/team-performance")
async def get_team_performance_analytics(
    department_id: Optional[uuid.UUID] = None,
    period: str = Query("6months", enum=["3months", "6months", "1year"]),
    current_user: models.User = Depends(require_roles(["admin", "hr_admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Get team performance analytics"""
    try:
        # Calculate date range
        period_days = {"3months": 90, "6months": 180, "1year": 365}
        start_date = datetime.utcnow() - timedelta(days=period_days[period])
        
        # Get employees to analyze
        employee_query = db.query(models.Employee).filter(models.Employee.is_active == True)
        if department_id:
            employee_query = employee_query.filter(models.Employee.department_id == department_id)
        elif current_user.role == "manager" and current_user.employee_id:
            # Managers see their direct reports
            employee_query = employee_query.filter(models.Employee.manager_id == current_user.employee_id)
        
        employees = employee_query.all()
        
        # Get performance reviews for these employees
        employee_ids = [emp.id for emp in employees]
        reviews = db.query(models.PerformanceReview).filter(
            and_(
                models.PerformanceReview.employee_id.in_(employee_ids),
                models.PerformanceReview.created_at >= start_date
            )
        ).all()
        
        # Calculate analytics
        total_employees = len(employees)
        total_reviews = len(reviews)
        
        # Rating distribution
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        if reviews:
            for review in reviews:
                if review.rating in rating_distribution:
                    rating_distribution[review.rating] += 1
        
        # Average rating
        avg_rating = None
        if reviews:
            avg_rating = sum([r.rating for r in reviews]) / len(reviews)
        
        # Top performers (rating >= 4)
        top_performers = [r for r in reviews if r.rating >= 4]
        top_performer_rate = (len(top_performers) / total_reviews * 100) if total_reviews > 0 else 0
        
        # Feedback metrics
        feedback_count = db.query(models.Feedback).filter(
            and_(
                models.Feedback.recipient_id.in_(employee_ids),
                models.Feedback.created_at >= start_date
            )
        ).count()
        
        feedback_per_employee = feedback_count / total_employees if total_employees > 0 else 0
        
        return {
            "team_analytics": {
                "total_employees": total_employees,
                "total_reviews": total_reviews,
                "average_rating": round(avg_rating, 2) if avg_rating else None,
                "top_performer_rate": round(top_performer_rate, 2),
                "feedback_count": feedback_count,
                "feedback_per_employee": round(feedback_per_employee, 2)
            },
            "rating_distribution": rating_distribution,
            "period": period,
            "department_id": str(department_id) if department_id else None,
            "analysis_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get team performance analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve team performance analytics"
        )

@router.get("/analytics/feedback-culture")
async def get_feedback_culture_metrics(
    department_id: Optional[uuid.UUID] = None,
    current_user: models.User = Depends(require_roles(["admin", "hr_admin"])),
    db: Session = Depends(get_db)
):
    """Get feedback culture metrics and insights"""
    try:
        # Base feedback query
        feedback_query = db.query(models.Feedback)
        
        if department_id:
            feedback_query = feedback_query.join(
                models.Employee, models.Feedback.recipient_id == models.Employee.id
            ).filter(models.Employee.department_id == department_id)
        
        all_feedback = feedback_query.all()
        
        # Calculate metrics
        total_feedback = len(all_feedback)
        
        # Feedback frequency (last 30 days)
        recent_feedback = [f for f in all_feedback if f.created_at >= datetime.utcnow() - timedelta(days=30)]
        feedback_velocity = len(recent_feedback)
        
        # Feedback type distribution
        type_distribution = {"peer": 0, "upward": 0, "downward": 0, "self": 0}
        for feedback in all_feedback:
            if feedback.feedback_type in type_distribution:
                type_distribution[feedback.feedback_type] += 1
        
        # Anonymous vs. identified feedback
        anonymous_count = len([f for f in all_feedback if f.is_anonymous])
        anonymous_rate = (anonymous_count / total_feedback * 100) if total_feedback > 0 else 0
        
        # Average feedback quality (based on ratings)
        rated_feedback = [f for f in all_feedback if f.rating is not None]
        avg_feedback_quality = sum([f.rating for f in rated_feedback]) / len(rated_feedback) if rated_feedback else None
        
        # Most active feedback givers
        giver_stats = {}
        for feedback in all_feedback:
            if feedback.giver_id not in giver_stats:
                giver_stats[feedback.giver_id] = 0
            giver_stats[feedback.giver_id] += 1
        
        top_givers = sorted(giver_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "feedback_culture_metrics": {
                "total_feedback_count": total_feedback,
                "monthly_feedback_velocity": feedback_velocity,
                "anonymous_feedback_rate": round(anonymous_rate, 2),
                "average_feedback_quality": round(avg_feedback_quality, 2) if avg_feedback_quality else None
            },
            "distributions": {
                "by_feedback_type": type_distribution
            },
            "engagement_indicators": {
                "top_feedback_givers": len(top_givers),
                "feedback_participation_rate": round((len(giver_stats) / db.query(models.Employee).filter(models.Employee.is_active == True).count() * 100), 2)
            },
            "analysis_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get feedback culture metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve feedback culture metrics"
        )

# =============================================================================
# AI-POWERED PERFORMANCE INSIGHTS
# =============================================================================

@router.post("/ai/generate-insights")
async def generate_ai_performance_insights(
    employee_data: Dict[str, Any],
    performance_history: List[Dict[str, Any]],
    current_user: models.User = Depends(require_roles(["admin", "hr_admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Generate AI-powered performance insights - matches frontend API call"""
    try:
        # Generate AI insights using Cerebras
        ai_insights = ai_service.generate_performance_insights(
            employee_data=employee_data,
            performance_history=performance_history
        )
        
        return {
            "success": True,
            "message": "AI performance insights generated successfully",
            "data": ai_insights,
            "ai_model": "Cerebras Llama-3.3-70B",
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate AI performance insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI performance insights: {str(e)}"
        )