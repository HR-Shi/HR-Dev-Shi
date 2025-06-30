from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
from ..database import get_db
from ..models import Survey, PerformanceReview, Employee, Department
from ..auth import get_current_user

router = APIRouter()

@router.get("/analytics")
async def get_analytics_data(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Calculate survey response rate
        total_surveys = db.query(Survey).count()
        completed_surveys = db.query(Survey).filter(Survey.status == "completed").count()
        survey_response_rate = (completed_surveys / total_surveys * 100) if total_surveys > 0 else 0

        # Calculate average performance rating
        reviews = db.query(PerformanceReview).all()
        average_rating = sum(review.rating for review in reviews) / len(reviews) if reviews else 0

        # Calculate employee satisfaction (example metric)
        employee_satisfaction = 85  # This would be calculated based on survey responses

        # Count active goals
        active_goals = db.query(PerformanceReview).filter(
            PerformanceReview.status == "in_progress"
        ).count()

        # Get department performance data
        departments = db.query(Department).all()
        department_performance = [
            {
                "name": dept.name,
                "value": sum(review.rating for review in dept.employees[0].reviews) / len(dept.employees[0].reviews)
                if dept.employees and dept.employees[0].reviews else 0
            }
            for dept in departments
        ]

        # Get survey distribution data
        survey_types = db.query(Survey.type).distinct().all()
        survey_distribution = [
            {
                "name": survey_type[0],
                "value": db.query(Survey).filter(Survey.type == survey_type[0]).count()
            }
            for survey_type in survey_types
        ]

        # Get performance trends (last 6 months)
        six_months_ago = datetime.now() - timedelta(days=180)
        monthly_reviews = db.query(PerformanceReview).filter(
            PerformanceReview.created_at >= six_months_ago
        ).all()

        performance_trends = []
        for i in range(6):
            month = datetime.now() - timedelta(days=30 * i)
            month_reviews = [r for r in monthly_reviews if r.created_at.month == month.month]
            avg_rating = sum(r.rating for r in month_reviews) / len(month_reviews) if month_reviews else 0
            performance_trends.append({
                "name": month.strftime("%b %Y"),
                "value": avg_rating
            })
        performance_trends.reverse()

        # Get employee engagement data
        engagement_metrics = [
            {"name": "High Engagement", "value": 65},
            {"name": "Medium Engagement", "value": 25},
            {"name": "Low Engagement", "value": 10}
        ]

        return {
            "surveyResponseRate": round(survey_response_rate, 1),
            "averagePerformanceRating": round(average_rating, 1),
            "employeeSatisfaction": employee_satisfaction,
            "activeGoals": active_goals,
            "departmentPerformance": department_performance,
            "surveyDistribution": survey_distribution,
            "performanceTrends": performance_trends,
            "employeeEngagement": engagement_metrics
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 