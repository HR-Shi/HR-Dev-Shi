from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models
import schemas
from auth.dependencies import get_current_active_user, require_roles
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, func, distinct
import uuid
from ai_service import ai_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/surveys",
    tags=["Surveys"]
)

# Helper function for manager+ access
def require_manager_access(current_user: models.User = Depends(get_current_active_user)):
    if current_user.role not in ["admin", "hr_admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    return current_user

# Helper function for admin access
def require_admin_access(current_user: models.User = Depends(get_current_active_user)):
    if current_user.role not in ["admin", "hr_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# =====================================================
# SURVEY TEMPLATES ENDPOINTS
# =====================================================

@router.get("/templates", response_model=List[schemas.SurveyTemplate])
async def get_survey_templates(
    category: Optional[str] = Query(None),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all survey templates with optional category filtering"""
    query = select(models.SurveyTemplate)
    if category:
        query = query.where(models.SurveyTemplate.category == category)
    
    result = await db.execute(query.order_by(models.SurveyTemplate.created_at.desc()))
    return result.scalars().all()

@router.post("/templates", response_model=schemas.SurveyTemplate)
async def create_survey_template(
    template: schemas.SurveyTemplateCreate,
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Create a new survey template (Admin only)"""
    try:
        template_data = template.dict()
        template_data["created_by"] = current_user.id
        
        db_template = models.SurveyTemplate(**template_data)
        db.add(db_template)
        await db.commit()
        await db.refresh(db_template)
        
        logger.info(f"Survey template created by {current_user.email}: {template.name}")
        return db_template
        
    except Exception as e:
        logger.error(f"Failed to create survey template: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create survey template"
        )

@router.post("/templates/{template_id}/use", response_model=schemas.Survey)
async def create_survey_from_template(
    template_id: uuid.UUID,
    survey_data: schemas.SurveyCreate,
    current_user: models.User = Depends(require_manager_access),
    db: Session = Depends(get_db)
):
    """Create a survey from a template"""
    try:
        # Get template
        template_result = await db.execute(
            select(models.SurveyTemplate).where(models.SurveyTemplate.id == template_id)
        )
        template = template_result.scalar_one_or_none()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Create survey with template questions
        survey_dict = survey_data.dict()
        survey_dict["questions"] = template.questions
        
        db_survey = models.Survey(**survey_dict)
        db.add(db_survey)
        await db.commit()
        await db.refresh(db_survey)
        
        logger.info(f"Survey created from template {template_id} by {current_user.email}: {survey_data.title}")
        return db_survey
        
    except Exception as e:
        logger.error(f"Failed to create survey from template: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create survey from template"
        )

# =====================================================
# SURVEY MAIN ENDPOINTS
# =====================================================

@router.get("/", response_model=List[schemas.Survey])
async def get_surveys(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    survey_type: Optional[str] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all surveys with filtering"""
    try:
        query = db.query(models.Survey)
        
        # Apply filters
        if is_active is not None:
            query = query.filter(models.Survey.is_active == is_active)
        if survey_type:
            query = query.filter(models.Survey.survey_type == survey_type)
        
        surveys = query.offset(skip).limit(limit).all()
        return surveys
        
    except Exception as e:
        logger.error(f"Failed to get surveys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve surveys"
        )

@router.get("/{survey_id}", response_model=schemas.Survey)
async def get_survey(
    survey_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific survey"""
    try:
        survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        return survey
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get survey {survey_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve survey"
        )

@router.post("/", response_model=schemas.Survey)
async def create_survey(
    survey: schemas.SurveyCreate,
    current_user: models.User = Depends(require_manager_access),
    db: Session = Depends(get_db)
):
    """Create a new survey (Manager+ access)"""
    try:
        # Create survey
        db_survey = models.Survey(**survey.dict(exclude={'questions'}))
        db.add(db_survey)
        db.commit()
        db.refresh(db_survey)
        
        # Add questions if provided
        if survey.questions:
            for question_data in survey.questions:
                question = models.SurveyQuestion(
                    survey_id=db_survey.id,
                    **question_data.dict()
                )
                db.add(question)
        
        db.commit()
        
        logger.info(f"Survey created by {current_user.email}: {survey.title}")
        return db_survey
        
    except Exception as e:
        logger.error(f"Failed to create survey: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create survey"
        )

@router.put("/{survey_id}", response_model=schemas.Survey)
async def update_survey(
    survey_id: str,
    survey_update: schemas.SurveyUpdate,
    current_user: models.User = Depends(require_manager_access),
    db: Session = Depends(get_db)
):
    """Update a survey (Manager+ access)"""
    try:
        survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        # Update fields
        for field, value in survey_update.dict(exclude_unset=True).items():
            setattr(survey, field, value)
        
        db.commit()
        db.refresh(survey)
        
        logger.info(f"Survey updated by {current_user.email}: {survey.title}")
        return survey
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update survey {survey_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update survey"
        )

@router.delete("/{survey_id}")
async def delete_survey(
    survey_id: str,
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Delete a survey (Admin only)"""
    try:
        survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        db.delete(survey)
        db.commit()
        
        logger.info(f"Survey deleted by {current_user.email}: {survey.title}")
        return {"message": "Survey deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete survey {survey_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete survey"
        )

# =====================================================
# SURVEY QUESTIONS ENDPOINTS
# =====================================================

@router.get("/{survey_id}/questions", response_model=List[schemas.SurveyQuestion])
async def get_survey_questions(
    survey_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all questions for a survey"""
    try:
        # Check if survey exists
        survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        questions = db.query(models.SurveyQuestion).filter(
            models.SurveyQuestion.survey_id == survey_id
        ).order_by(models.SurveyQuestion.order).all()
        
        return questions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get questions for survey {survey_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve survey questions"
        )

@router.post("/{survey_id}/questions", response_model=schemas.SurveyQuestion)
async def add_survey_question(
    survey_id: str,
    question: schemas.SurveyQuestionCreate,
    current_user: models.User = Depends(require_manager_access),
    db: Session = Depends(get_db)
):
    """Add a question to a survey (Manager+ access)"""
    try:
        # Check if survey exists
        survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        db_question = models.SurveyQuestion(
            survey_id=survey_id,
            **question.dict()
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        
        logger.info(f"Question added to survey {survey_id} by {current_user.email}")
        return db_question
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add question to survey {survey_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add survey question"
        )

# =====================================================
# SURVEY RESPONSES ENDPOINTS
# =====================================================

@router.post("/{survey_id}/responses", response_model=schemas.SurveyResponse)
async def submit_survey_response(
    survey_id: str,
    response: schemas.SurveyResponseCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit a response to a survey"""
    try:
        # Check if survey exists
        survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        # Check if survey is active
        if not survey.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Survey is not active"
            )
        
        # Check if user already responded
        existing_response = db.query(models.SurveyResponse).filter(
            models.SurveyResponse.survey_id == survey_id,
            models.SurveyResponse.employee_id == current_user.employee_id
        ).first()
        
        if existing_response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Response already submitted"
            )
        
        # Create response
        db_response = models.SurveyResponse(
            survey_id=survey_id,
            employee_id=current_user.employee_id,
            **response.dict()
        )
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        
        logger.info(f"Survey response submitted by {current_user.email} for survey {survey_id}")
        return db_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit survey response: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit survey response"
        )

@router.get("/{survey_id}/responses", response_model=List[schemas.SurveyResponse])
async def get_survey_responses(
    survey_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User = Depends(require_manager_access),
    db: Session = Depends(get_db)
):
    """Get all responses for a survey (Manager+ access)"""
    try:
        # Check if survey exists
        survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        responses = db.query(models.SurveyResponse).filter(
            models.SurveyResponse.survey_id == survey_id
        ).offset(skip).limit(limit).all()
        
        return responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get responses for survey {survey_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve survey responses"
        )

@router.get("/{survey_id}/analytics")
async def get_survey_analytics(
    survey_id: str,
    current_user: models.User = Depends(require_manager_access),
    db: Session = Depends(get_db)
):
    """Get analytics for a survey (Manager+ access)"""
    try:
        # Check if survey exists
        survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        # Get response statistics
        total_responses = db.query(models.SurveyResponse).filter(
            models.SurveyResponse.survey_id == survey_id
        ).count()
        
        # Get completion rate (if we have target employees)
        target_count = len(survey.target_employees) if survey.target_employees else 0
        completion_rate = (total_responses / target_count * 100) if target_count > 0 else 0
        
        # Get response distribution by department
        dept_responses = db.execute("""
            SELECT d.name, COUNT(sr.id) as response_count
            FROM survey_responses sr
            JOIN employees e ON sr.employee_id = e.id
            JOIN departments d ON e.department_id = d.id
            WHERE sr.survey_id = :survey_id
            GROUP BY d.name
        """, {"survey_id": survey_id}).fetchall()
        
        analytics = {
            "survey_id": survey_id,
            "survey_title": survey.title,
            "total_responses": total_responses,
            "target_employees": target_count,
            "completion_rate": round(completion_rate, 2),
            "response_by_department": [
                {"department": dept[0], "responses": dept[1]}
                for dept in dept_responses
            ],
            "last_response": db.query(models.SurveyResponse).filter(
                models.SurveyResponse.survey_id == survey_id
            ).order_by(models.SurveyResponse.created_at.desc()).first().created_at if total_responses > 0 else None
        }
        
        return {
            "success": True,
            "message": "Survey analytics retrieved successfully",
            "data": analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analytics for survey {survey_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve survey analytics"
        )

@router.get("/stats/summary")
async def get_survey_stats(
    current_user: models.User = Depends(require_manager_access),
    db: Session = Depends(get_db)
):
    """Get survey statistics (Manager+ access)"""
    try:
        stats = {
            "total_surveys": db.query(models.Survey).count(),
            "active_surveys": db.query(models.Survey).filter(models.Survey.is_active == True).count(),
            "total_responses": db.query(models.SurveyResponse).count(),
            "survey_templates": db.query(models.SurveyTemplate).count(),
        }
        
        # Get surveys by type
        survey_types = db.execute("""
            SELECT survey_type, COUNT(*) as count
            FROM surveys
            GROUP BY survey_type
        """).fetchall()
        
        stats["by_type"] = {stype[0]: stype[1] for stype in survey_types}
        
        return {
            "success": True,
            "message": "Survey statistics retrieved successfully",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get survey stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve survey statistics"
        )

# Question Bank Operations
@router.get("/question-bank")
async def get_question_bank(
    category: Optional[str] = Query(None),
    kpi_category: Optional[str] = Query(None),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get predefined question bank for survey creation"""
    question_bank = {
        "employee_engagement": [
            {"text": "How satisfied are you with your current role?", "type": "scale", "scale": 5},
            {"text": "How likely are you to recommend this company as a place to work?", "type": "scale", "scale": 10},
            {"text": "Do you feel your work has meaning and purpose?", "type": "scale", "scale": 5},
            {"text": "How well does your manager support your professional development?", "type": "scale", "scale": 5},
            {"text": "How effectively does leadership communicate company vision?", "type": "scale", "scale": 5},
        ],
        "well_being": [
            {"text": "How would you rate your current stress level at work?", "type": "scale", "scale": 5},
            {"text": "How manageable is your current workload?", "type": "scale", "scale": 5},
            {"text": "How satisfied are you with your work-life balance?", "type": "scale", "scale": 5},
            {"text": "Do you feel you have adequate support from your team?", "type": "boolean"},
            {"text": "How would you rate the physical work environment?", "type": "scale", "scale": 5},
        ],
        "performance": [
            {"text": "How clear are your performance expectations?", "type": "scale", "scale": 5},
            {"text": "How frequently do you receive helpful feedback?", "type": "scale", "scale": 5},
            {"text": "How supported do you feel in achieving your goals?", "type": "scale", "scale": 5},
            {"text": "How satisfied are you with your professional development opportunities?", "type": "scale", "scale": 5},
        ],
        "diversity_inclusion": [
            {"text": "How included do you feel in your team?", "type": "scale", "scale": 5},
            {"text": "Do you feel your voice is heard and valued?", "type": "boolean"},
            {"text": "How fairly are you treated compared to your colleagues?", "type": "scale", "scale": 5},
            {"text": "How comfortable do you feel expressing your authentic self at work?", "type": "scale", "scale": 5},
        ]
    }
    
    if category and category in question_bank:
        return {"category": category, "questions": question_bank[category]}
    
    return {"all_categories": question_bank}

# Survey Scheduling Operations
@router.post("/{survey_id}/schedule")
async def schedule_survey(
    survey_id: uuid.UUID,
    schedule_data: dict = Body(...),
    current_user: models.User = Depends(require_manager_access),
    db: Session = Depends(get_db)
):
    """Schedule survey deployment with recurring options"""
    try:
        survey = await get_survey(survey_id, current_user)
        
        # Update survey with scheduling information
        schedule_config = {
            "start_date": schedule_data.get("start_date"),
            "end_date": schedule_data.get("end_date"),
            "frequency": schedule_data.get("frequency", "one-time"),
            "recurring_until": schedule_data.get("recurring_until"),
            "reminder_settings": schedule_data.get("reminder_settings", {}),
            "auto_deploy": schedule_data.get("auto_deploy", False)
        }
        
        survey.platform_integrations["scheduling"] = schedule_config
        survey.status = "scheduled"
        
        await db.commit()
        return {"message": "Survey scheduled successfully", "schedule": schedule_config}
        
    except Exception as e:
        logger.error(f"Failed to schedule survey: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule survey"
        )

# Platform Integration Operations
@router.post("/{survey_id}/integrations")
async def configure_platform_integrations(
    survey_id: uuid.UUID,
    integrations: dict = Body(...),
    current_user: models.User = Depends(require_manager_access),
    db: Session = Depends(get_db)
):
    """Configure platform integrations for survey distribution"""
    try:
        survey = await get_survey(survey_id, current_user)
        
        # Validate and configure integrations
        supported_platforms = ["slack", "teams", "zoom", "email"]
        configured_integrations = {}
        
        for platform, config in integrations.items():
            if platform not in supported_platforms:
                raise HTTPException(status_code=400, detail=f"Platform {platform} not supported")
            
            # Platform-specific configuration validation
            if platform == "slack":
                configured_integrations[platform] = {
                    "channel_ids": config.get("channel_ids", []),
                    "user_groups": config.get("user_groups", []),
                    "notification_type": config.get("notification_type", "message"),
                    "reminder_enabled": config.get("reminder_enabled", True)
                }
            elif platform == "teams":
                configured_integrations[platform] = {
                    "team_ids": config.get("team_ids", []),
                    "channel_ids": config.get("channel_ids", []),
                    "adaptive_card": config.get("adaptive_card", True)
                }
            elif platform == "zoom":
                configured_integrations[platform] = {
                    "meeting_types": config.get("meeting_types", ["all"]),
                    "post_meeting_survey": config.get("post_meeting_survey", True),
                    "meeting_id_filter": config.get("meeting_id_filter", [])
                }
            elif platform == "email":
                configured_integrations[platform] = {
                    "template_id": config.get("template_id"),
                    "sender_name": config.get("sender_name", "HR Team"),
                    "reminder_schedule": config.get("reminder_schedule", ["3_days", "1_day"])
                }
        
        survey.platform_integrations.update(configured_integrations)
        await db.commit()
        
        return {"message": "Platform integrations configured", "integrations": configured_integrations}
        
    except Exception as e:
        logger.error(f"Failed to configure platform integrations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to configure platform integrations"
        )

# Real-time Response Collection
@router.get("/{survey_id}/responses/real-time")
async def get_real_time_responses(
    survey_id: uuid.UUID,
    current_user: models.User = Depends(require_manager_access),
    db: Session = Depends(get_db)
):
    """Get real-time response aggregation and statistics"""
    try:
        survey = await get_survey(survey_id, current_user)
        
        # Get response statistics
        response_stats = await db.execute(
            select(
                func.count(models.SurveyResponse.id).label("total_responses"),
                func.count(distinct(models.SurveyResponse.employee_id)).label("unique_respondents"),
                func.avg(models.SurveyResponse.completion_time_seconds).label("avg_completion_time")
            ).where(models.SurveyResponse.survey_id == survey_id)
        )
        stats = response_stats.first()
        
        # Calculate response rate
        target_count = len(survey.target_employees) if survey.target_employees else 0
        response_rate = (stats.unique_respondents / target_count * 100) if target_count > 0 else 0
        
        # Get recent responses (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_responses = await db.execute(
            select(func.count(models.SurveyResponse.id))
            .where(
                models.SurveyResponse.survey_id == survey_id,
                models.SurveyResponse.submitted_at >= recent_cutoff
            )
        )
        
        return {
            "survey_id": survey_id,
            "total_responses": stats.total_responses or 0,
            "unique_respondents": stats.unique_respondents or 0,
            "response_rate": round(response_rate, 2),
            "avg_completion_time": round(stats.avg_completion_time or 0, 2),
            "recent_responses_24h": recent_responses.scalar() or 0,
            "target_count": target_count,
            "status": survey.status
        }
        
    except Exception as e:
        logger.error(f"Failed to get real-time responses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve real-time responses"
        )

# Survey Branching Logic
@router.post("/{survey_id}/branching")
async def configure_survey_branching(
    survey_id: uuid.UUID,
    branching_rules: dict = Body(...),
    current_user: models.User = Depends(require_manager_access),
    db: Session = Depends(get_db)
):
    """Configure conditional branching logic for surveys"""
    try:
        survey = await get_survey(survey_id, current_user)
        
        # Validate branching rules structure
        validated_rules = []
        for rule in branching_rules.get("rules", []):
            validated_rule = {
                "question_id": rule["question_id"],
                "condition": rule["condition"],  # equals, greater_than, contains, etc.
                "value": rule["value"],
                "action": rule["action"],  # show_question, skip_to, end_survey
                "target": rule.get("target")  # target question or section
            }
            validated_rules.append(validated_rule)
        
        # Store branching configuration
        survey.platform_integrations["branching"] = {
            "enabled": True,
            "rules": validated_rules,
            "default_flow": branching_rules.get("default_flow", "linear")
        }
        
        await db.commit()
        return {"message": "Branching logic configured", "rules": validated_rules}
        
    except Exception as e:
        logger.error(f"Failed to configure survey branching: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to configure survey branching"
        )

# Survey Quality & Validation
@router.get("/{survey_id}/quality-check")
async def perform_survey_quality_check(
    survey_id: uuid.UUID,
    current_user: models.User = Depends(require_manager_access),
    db: Session = Depends(get_db)
):
    """Perform comprehensive quality check on survey responses"""
    try:
        survey = await get_survey(survey_id, current_user)
        
        # Get all responses for analysis
        responses_result = await db.execute(
            select(models.SurveyResponse).where(models.SurveyResponse.survey_id == survey_id)
        )
        responses = responses_result.scalars().all()
        
        quality_metrics = {
            "total_responses": len(responses),
            "completion_rate": 0,
            "average_completion_time": 0,
            "response_quality_score": 0,
            "outlier_responses": [],
            "validation_flags": []
        }
        
        if responses:
            # Calculate completion metrics
            completion_times = [r.completion_time_seconds for r in responses if r.completion_time_seconds]
            if completion_times:
                quality_metrics["average_completion_time"] = sum(completion_times) / len(completion_times)
                
                # Identify outliers (responses too fast or too slow)
                median_time = sorted(completion_times)[len(completion_times) // 2]
                for i, response in enumerate(responses):
                    if response.completion_time_seconds:
                        if response.completion_time_seconds < median_time * 0.2:  # Too fast
                            quality_metrics["outlier_responses"].append({
                                "response_id": str(response.id),
                                "issue": "suspiciously_fast",
                                "completion_time": response.completion_time_seconds
                            })
                        elif response.completion_time_seconds > median_time * 5:  # Too slow
                            quality_metrics["outlier_responses"].append({
                                "response_id": str(response.id),
                                "issue": "unusually_slow",
                                "completion_time": response.completion_time_seconds
                            })
            
            # Response quality scoring
            quality_score = 100
            if len(quality_metrics["outlier_responses"]) > len(responses) * 0.1:
                quality_score -= 20
                quality_metrics["validation_flags"].append("high_outlier_rate")
            
            quality_metrics["response_quality_score"] = quality_score
        
        return quality_metrics
        
    except Exception as e:
        logger.error(f"Failed to perform survey quality check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform survey quality check"
        )

# =====================================================
# AI-POWERED ENDPOINTS
# =====================================================

@router.post("/ai/generate-questions")
async def generate_ai_survey_questions(
    kpi_focus: str = Query(..., description="The KPI or area to focus survey questions on"),
    survey_type: str = Query(..., description="Type of survey (pulse, engagement, etc.)"),
    current_user: models.User = Depends(require_manager_access),
    db: Session = Depends(get_db)
):
    """Generate AI-optimized survey questions using Cerebras"""
    try:
        # Generate AI survey questions using Cerebras
        ai_questions = ai_service.generate_survey_questions(
            kpi_focus=kpi_focus,
            survey_type=survey_type
        )
        
        return {
            "success": True,
            "message": "AI survey questions generated successfully",
            "data": {
                "kpi_focus": kpi_focus,
                "survey_type": survey_type,
                "ai_questions": ai_questions,
                "ai_model": "Cerebras Llama-3.3-70B",
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate AI survey questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI survey questions: {str(e)}"
        )

@router.post("/ai/analyze-sentiment")
async def analyze_survey_sentiment(
    survey_id: uuid.UUID,
    current_user: models.User = Depends(require_manager_access),
    db: Session = Depends(get_db)
):
    """Analyze sentiment of survey responses using AI"""
    try:
        # Get survey responses
        responses = db.query(models.SurveyResponse).filter(
            models.SurveyResponse.survey_id == survey_id
        ).all()
        
        if not responses:
            return {
                "success": False,
                "message": "No responses found for sentiment analysis",
                "data": None
            }
        
        # Extract text responses for sentiment analysis
        text_responses = []
        for response in responses:
            if response.responses and isinstance(response.responses, dict):
                for key, value in response.responses.items():
                    if isinstance(value, str) and len(value.strip()) > 10:
                        text_responses.append(value.strip())
        
        if not text_responses:
            return {
                "success": False,
                "message": "No text responses found for sentiment analysis",
                "data": None
            }
        
        # Analyze sentiment using AI service
        sentiment_analysis = ai_service.analyze_sentiment(text_responses)
        
        return {
            "success": True,
            "message": "Sentiment analysis completed successfully",
            "data": {
                "survey_id": str(survey_id),
                "total_responses": len(responses),
                "text_responses_analyzed": len(text_responses),
                "sentiment_analysis": sentiment_analysis,
                "ai_model": "Cerebras Llama-3.3-70B",
                "analyzed_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze survey sentiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze survey sentiment: {str(e)}"
        )