from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import models
import schemas
from database import get_db
from auth.dependencies import get_current_active_user, require_roles
from ai_service import ai_service
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai",
    tags=["AI Services"]
)

@router.post("/generate-action-plans")
async def generate_ai_action_plans(
    issue_type: str = Query(..., description="Type of issue to address"),
    department_id: Optional[uuid.UUID] = Query(None, description="Target department"),
    current_user: models.User = Depends(require_roles(["admin", "hr_admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Generate AI-powered action plan recommendations"""
    try:
        # Gather context data for AI
        context_data = {
            "issue_type": issue_type,
            "department_id": str(department_id) if department_id else None,
            "user_role": current_user.role
        }
        
        # Get relevant KPIs for context
        kpi_query = db.query(models.KPI).filter(models.KPI.is_active == True)
        if department_id:
            kpi_query = kpi_query.filter(
                models.KPI.department_id == department_id
            )
        kpis = kpi_query.limit(10).all()
        
        kpi_context = [
            {
                "name": kpi.name,
                "current_value": float(kpi.current_value) if kpi.current_value else 0,
                "target_value": float(kpi.target_value) if kpi.target_value else 0,
                "category": kpi.category
            }
            for kpi in kpis
        ]
        
        # Get recent survey data for context
        recent_surveys = db.query(models.Survey).filter(
            models.Survey.status == "completed"
        ).order_by(models.Survey.created_at.desc()).limit(3).all()
        
        survey_context = [
            {
                "title": survey.title,
                "type": survey.type,
                "response_count": db.query(models.SurveyResponse).filter(
                    models.SurveyResponse.survey_id == survey.id
                ).count()
            }
            for survey in recent_surveys
        ]
        
        # Generate AI recommendations
        try:
            recommendations = ai_service.generate_action_plan_templates(
                issue_type=issue_type,
                kpi_data={"kpis": kpi_context},
                survey_data={"surveys": survey_context},
                department_context=context_data
            )
            
            return {
                "success": True,
                "message": "AI action plan recommendations generated successfully",
                "data": {
                    "issue_type": issue_type,
                    "department_id": str(department_id) if department_id else None,
                    "recommendations": recommendations,
                    "context": {
                        "kpis_analyzed": len(kpi_context),
                        "surveys_analyzed": len(survey_context)
                    },
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as ai_error:
            logger.warning(f"AI service failed, providing fallback recommendations: {ai_error}")
            
            # Fallback recommendations when AI service is not available
            fallback_recommendations = get_fallback_action_plans(issue_type)
            
            return {
                "success": True,
                "message": "Action plan recommendations generated (fallback mode)",
                "data": {
                    "issue_type": issue_type,
                    "department_id": str(department_id) if department_id else None,
                    "recommendations": fallback_recommendations,
                    "context": {
                        "kpis_analyzed": len(kpi_context),
                        "surveys_analyzed": len(survey_context)
                    },
                    "generated_at": datetime.utcnow().isoformat(),
                    "fallback_mode": True
                }
            }
            
    except Exception as e:
        logger.error(f"Failed to generate action plan recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

@router.post("/analyze-sentiment")
async def analyze_survey_sentiment(
    survey_id: uuid.UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze sentiment of survey responses"""
    try:
        # Get survey responses
        responses = db.query(models.SurveyResponse).filter(
            models.SurveyResponse.survey_id == survey_id
        ).all()
        
        if not responses:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No survey responses found"
            )
        
        # Extract text responses for sentiment analysis
        text_responses = []
        for response in responses:
            if response.responses and isinstance(response.responses, dict):
                for key, value in response.responses.items():
                    if isinstance(value, str) and len(value.strip()) > 10:
                        text_responses.append(value)
        
        if not text_responses:
            return {
                "success": True,
                "message": "No text responses found for sentiment analysis",
                "data": {
                    "survey_id": str(survey_id),
                    "total_responses": len(responses),
                    "text_responses": 0,
                    "sentiment_analysis": None
                }
            }
        
        try:
            # Use AI service for sentiment analysis
            sentiment_results = ai_service.analyze_sentiment(text_responses)
            
            return {
                "success": True,
                "message": "Sentiment analysis completed",
                "data": {
                    "survey_id": str(survey_id),
                    "total_responses": len(responses),
                    "text_responses": len(text_responses),
                    "sentiment_analysis": sentiment_results,
                    "analyzed_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as ai_error:
            logger.warning(f"AI sentiment analysis failed: {ai_error}")
            
            # Fallback sentiment analysis
            fallback_sentiment = {
                "overall_sentiment": "neutral",
                "positive_percentage": 33.3,
                "neutral_percentage": 33.3,
                "negative_percentage": 33.3,
                "key_themes": ["communication", "work-life balance", "professional development"],
                "fallback_mode": True
            }
            
            return {
                "success": True,
                "message": "Sentiment analysis completed (fallback mode)",
                "data": {
                    "survey_id": str(survey_id),
                    "total_responses": len(responses),
                    "text_responses": len(text_responses),
                    "sentiment_analysis": fallback_sentiment,
                    "analyzed_at": datetime.utcnow().isoformat()
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze sentiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze sentiment: {str(e)}"
        )

def get_fallback_action_plans(issue_type: str) -> List[Dict[str, Any]]:
    """Get fallback action plan recommendations when AI service is unavailable"""
    
    fallback_plans = {
        "low_engagement": [
            {
                "title": "Team Building Workshop",
                "description": "Organize interactive team building activities to improve collaboration and morale",
                "category": "engagement",
                "estimated_duration_days": 30,
                "steps": [
                    {"step": 1, "title": "Plan activities", "duration": 7},
                    {"step": 2, "title": "Book venue", "duration": 3},
                    {"step": 3, "title": "Execute workshop", "duration": 1},
                    {"step": 4, "title": "Follow-up survey", "duration": 7}
                ],
                "priority": "high",
                "success_metrics": ["engagement_score_increase", "team_satisfaction"]
            },
            {
                "title": "One-on-One Meeting Enhancement",
                "description": "Improve manager-employee relationships through structured 1:1 meetings",
                "category": "engagement",
                "estimated_duration_days": 60,
                "steps": [
                    {"step": 1, "title": "Train managers", "duration": 14},
                    {"step": 2, "title": "Schedule regular 1:1s", "duration": 7},
                    {"step": 3, "title": "Monitor progress", "duration": 30}
                ],
                "priority": "medium",
                "success_metrics": ["manager_effectiveness", "employee_satisfaction"]
            }
        ],
        "high_stress": [
            {
                "title": "Workplace Wellness Program",
                "description": "Implement comprehensive wellness initiatives to reduce employee stress",
                "category": "wellbeing",
                "estimated_duration_days": 90,
                "steps": [
                    {"step": 1, "title": "Assess stress factors", "duration": 14},
                    {"step": 2, "title": "Design wellness program", "duration": 21},
                    {"step": 3, "title": "Launch initiatives", "duration": 7},
                    {"step": 4, "title": "Monitor and adjust", "duration": 48}
                ],
                "priority": "high",
                "success_metrics": ["stress_level_reduction", "work_life_balance"]
            }
        ],
        "poor_performance": [
            {
                "title": "Performance Improvement Plan",
                "description": "Structured approach to help underperforming employees succeed",
                "category": "performance",
                "estimated_duration_days": 90,
                "steps": [
                    {"step": 1, "title": "Identify performance gaps", "duration": 7},
                    {"step": 2, "title": "Create improvement plan", "duration": 7},
                    {"step": 3, "title": "Provide training/support", "duration": 30},
                    {"step": 4, "title": "Monitor progress", "duration": 46}
                ],
                "priority": "high",
                "success_metrics": ["performance_improvement", "goal_achievement"]
            }
        ]
    }
    
    return fallback_plans.get(issue_type, [
        {
            "title": "General Improvement Initiative",
            "description": f"Comprehensive approach to address {issue_type} issues",
            "category": "general",
            "estimated_duration_days": 60,
            "steps": [
                {"step": 1, "title": "Assess current situation", "duration": 14},
                {"step": 2, "title": "Design intervention", "duration": 14},
                {"step": 3, "title": "Implement changes", "duration": 21},
                {"step": 4, "title": "Measure results", "duration": 11}
            ],
            "priority": "medium",
            "success_metrics": ["overall_improvement", "stakeholder_satisfaction"]
        }
    ]) 