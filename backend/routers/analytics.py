from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc, text
from typing import List, Optional, Dict, Any, Union
import models
import schemas
from database import get_db
from auth.dependencies import get_current_active_user, require_roles
from ai_service import ai_service
import logging
from datetime import datetime, timedelta
import uuid
import pandas as pd
import numpy as np
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

# =============================================================================
# REAL-TIME ANALYTICS DASHBOARD
# =============================================================================

@router.get("/dashboard/overview")
async def get_dashboard_overview(
    department_id: Optional[uuid.UUID] = None,
    period: str = Query("3months", enum=["1month", "3months", "6months", "1year"]),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard overview with real-time KPI tracking"""
    try:
        # Calculate date range
        period_days = {"1month": 30, "3months": 90, "6months": 180, "1year": 365}
        start_date = datetime.utcnow() - timedelta(days=period_days[period])
        
        # Apply user role-based filtering
        department_filter = None
        if current_user.role == "manager":
            if current_user.employee_id:
                employee = db.query(models.Employee).filter(models.Employee.id == current_user.employee_id).first()
                if employee and employee.department_id:
                    department_filter = employee.department_id
        elif department_id:
            department_filter = department_id
        
        # Get KPI summary
        kpi_query = db.query(models.KPI).filter(models.KPI.is_active == True)
        if department_filter:
            kpi_query = kpi_query.filter(
                or_(
                    models.KPI.department_id == department_filter,
                    models.KPI.department_id.is_(None)
                )
            )
        
        kpis = kpi_query.all()
        
        # Calculate KPI metrics
        total_kpis = len(kpis)
        kpis_on_target = 0
        kpis_off_target = 0
        kpis_trending_up = 0
        kpis_trending_down = 0
        critical_alerts = []
        
        for kpi in kpis:
            # Target achievement
            if kpi.current_value is not None and kpi.target_value is not None:
                deviation_pct = abs(kpi.current_value - kpi.target_value) / kpi.target_value * 100
                if deviation_pct <= 5:  # Within 5%
                    kpis_on_target += 1
                else:
                    kpis_off_target += 1
                    
                # Critical alerts (>20% deviation)
                if deviation_pct > 20:
                    critical_alerts.append({
                        "kpi_id": kpi.id,
                        "kpi_name": kpi.name,
                        "current_value": kpi.current_value,
                        "target_value": kpi.target_value,
                        "deviation_percentage": round(deviation_pct, 2),
                        "priority": kpi.priority
                    })
            
            # Trend analysis (last 5 measurements)
            recent_measurements = db.query(models.KPIMeasurement).filter(
                models.KPIMeasurement.kpi_id == kpi.id
            ).order_by(desc(models.KPIMeasurement.measurement_date)).limit(5).all()
            
            if len(recent_measurements) >= 3:
                values = [m.value for m in reversed(recent_measurements)]
                trend = calculate_trend(values)
                if trend > 0.05:  # 5% improvement
                    kpis_trending_up += 1
                elif trend < -0.05:  # 5% decline
                    kpis_trending_down += 1
        
        # Employee metrics
        employee_query = db.query(models.Employee).filter(models.Employee.is_active == True)
        if department_filter:
            employee_query = employee_query.filter(models.Employee.department_id == department_filter)
        
        total_employees = employee_query.count()
        
        # Survey response rates
        recent_surveys = db.query(models.Survey).filter(
            and_(
                models.Survey.start_date >= start_date,
                models.Survey.status == "active"
            )
        )
        if department_filter:
            recent_surveys = recent_surveys.filter(
                models.Survey.target_departments.contains(str(department_filter))
            )
        
        survey_response_rate = 0
        if recent_surveys.count() > 0:
            total_responses = db.query(models.SurveyResponse).join(
                models.Survey, models.SurveyResponse.survey_id == models.Survey.id
            ).filter(models.Survey.start_date >= start_date).count()
            
            expected_responses = recent_surveys.count() * total_employees
            survey_response_rate = (total_responses / expected_responses * 100) if expected_responses > 0 else 0
        
        # Action Plan metrics
        action_plan_query = db.query(models.ActionPlan)
        if department_filter:
            action_plan_query = action_plan_query.filter(
                models.ActionPlan.target_departments.contains(str(department_filter))
            )
        
        total_action_plans = action_plan_query.count()
        completed_action_plans = action_plan_query.filter(
            models.ActionPlan.status == "completed"
        ).count()
        
        action_plan_completion_rate = (completed_action_plans / total_action_plans * 100) if total_action_plans > 0 else 0
        
        # Focus Group metrics
        focus_group_query = db.query(models.FocusGroup).filter(models.FocusGroup.status == "active")
        if department_filter:
            focus_group_query = focus_group_query.filter(models.FocusGroup.department_id == department_filter)
        
        active_focus_groups = focus_group_query.count()
        
        return {
            "overview": {
                "kpi_summary": {
                    "total_kpis": total_kpis,
                    "kpis_on_target": kpis_on_target,
                    "kpis_off_target": kpis_off_target,
                    "target_achievement_rate": round((kpis_on_target / total_kpis * 100), 2) if total_kpis > 0 else 0,
                    "kpis_trending_up": kpis_trending_up,
                    "kpis_trending_down": kpis_trending_down
                },
                "employee_metrics": {
                    "total_employees": total_employees,
                    "survey_response_rate": round(survey_response_rate, 2),
                    "active_focus_groups": active_focus_groups
                },
                "action_plan_metrics": {
                    "total_action_plans": total_action_plans,
                    "completed_action_plans": completed_action_plans,
                    "completion_rate": round(action_plan_completion_rate, 2)
                }
            },
            "alerts": {
                "critical_kpis": critical_alerts[:5],  # Top 5 critical alerts
                "total_alerts": len(critical_alerts)
            },
            "period": period,
            "department_filter": str(department_filter) if department_filter else None,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard overview"
        )

@router.get("/dashboard/charts/kpi-trends")
async def get_kpi_trend_charts(
    kpi_ids: Optional[str] = None,  # Comma-separated KPI IDs
    period: str = Query("3months", enum=["1month", "3months", "6months", "1year"]),
    department_id: Optional[uuid.UUID] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get KPI trend charts data for interactive visualization"""
    try:
        # Calculate date range
        period_days = {"1month": 30, "3months": 90, "6months": 180, "1year": 365}
        start_date = datetime.utcnow() - timedelta(days=period_days[period])
        
        # Parse KPI IDs
        if kpi_ids:
            kpi_id_list = [uuid.UUID(id.strip()) for id in kpi_ids.split(',')]
        else:
            # Get top 5 KPIs by priority and activity
            kpi_query = db.query(models.KPI).filter(models.KPI.is_active == True)
            if department_id:
                kpi_query = kpi_query.filter(
                    or_(
                        models.KPI.department_id == department_id,
                        models.KPI.department_id.is_(None)
                    )
                )
            
            top_kpis = kpi_query.order_by(
                func.case(
                    (models.KPI.priority == "high", 1),
                    (models.KPI.priority == "medium", 2),
                    (models.KPI.priority == "low", 3),
                    else_=4
                )
            ).limit(5).all()
            
            kpi_id_list = [kpi.id for kpi in top_kpis]
        
        # Get KPI data and measurements
        chart_data = []
        
        for kpi_id in kpi_id_list:
            kpi = db.query(models.KPI).filter(models.KPI.id == kpi_id).first()
            if not kpi:
                continue
            
            # Get measurements for the period
            measurements = db.query(models.KPIMeasurement).filter(
                and_(
                    models.KPIMeasurement.kpi_id == kpi_id,
                    models.KPIMeasurement.measurement_date >= start_date
                )
            ).order_by(models.KPIMeasurement.measurement_date).all()
            
            # Prepare data points
            data_points = [
                {
                    "date": m.measurement_date.isoformat(),
                    "value": m.value,
                    "target": kpi.target_value,
                    "notes": m.notes
                }
                for m in measurements
            ]
            
            # Calculate trend
            values = [m.value for m in measurements]
            trend = calculate_trend(values) if len(values) >= 2 else 0
            
            chart_data.append({
                "kpi_id": kpi.id,
                "kpi_name": kpi.name,
                "category": kpi.category,
                "measurement_type": kpi.measurement_type,
                "target_value": kpi.target_value,
                "current_value": kpi.current_value,
                "trend_percentage": round(trend * 100, 2),
                "data_points": data_points,
                "color": get_kpi_color(kpi.category)
            })
        
        return {
            "charts": chart_data,
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get KPI trend charts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve KPI trend charts"
        )

@router.get("/dashboard/charts/heatmap")
async def get_department_heatmap(
    metric: str = Query("engagement", enum=["engagement", "performance", "satisfaction", "turnover"]),
    period: str = Query("3months", enum=["1month", "3months", "6months", "1year"]),
    current_user: models.User = Depends(require_roles(["admin", "hr_admin"])),
    db: Session = Depends(get_db)
):
    """Get department performance heatmap data"""
    try:
        # Get all departments
        departments = db.query(models.Department).all()
        
        heatmap_data = []
        
        for dept in departments:
            # Get department employees
            employee_count = db.query(models.Employee).filter(
                and_(
                    models.Employee.department_id == dept.id,
                    models.Employee.is_active == True
                )
            ).count()
            
            if employee_count == 0:
                continue
            
            # Calculate metric based on type
            metric_value = 0
            
            if metric == "engagement":
                # Get average engagement score from recent surveys
                engagement_scores = db.execute(text("""
                    SELECT AVG(CAST(responses->>'engagement_score' AS FLOAT)) as avg_score
                    FROM survey_responses sr
                    JOIN surveys s ON sr.survey_id = s.id
                    JOIN employees e ON sr.employee_id = e.id
                    WHERE e.department_id = :dept_id
                    AND s.start_date >= :start_date
                    AND responses->>'engagement_score' IS NOT NULL
                """), {
                    "dept_id": dept.id,
                    "start_date": datetime.utcnow() - timedelta(days=90)
                }).fetchone()
                
                metric_value = engagement_scores[0] if engagement_scores and engagement_scores[0] else 65
                
            elif metric == "turnover":
                # Calculate turnover rate
                period_days = {"1month": 30, "3months": 90, "6months": 180, "1year": 365}
                start_date = datetime.utcnow() - timedelta(days=period_days[period])
                
                left_employees = db.query(models.Employee).filter(
                    and_(
                        models.Employee.department_id == dept.id,
                        models.Employee.status == "terminated",
                        models.Employee.updated_at >= start_date
                    )
                ).count()
                
                metric_value = (left_employees / employee_count * 100) if employee_count > 0 else 0
            
            # Determine intensity based on metric
            if metric == "turnover":
                # Lower is better for turnover
                intensity = min(metric_value / 20, 1.0)  # 20% turnover = max intensity
            else:
                # Higher is better for other metrics
                intensity = max(0, min(metric_value / 100, 1.0))
            
            heatmap_data.append({
                "department_id": dept.id,
                "department_name": dept.name,
                "metric_value": round(metric_value, 2),
                "intensity": round(intensity, 2),
                "employee_count": employee_count,
                "color": get_heatmap_color(intensity)
            })
        
        return {
            "heatmap_data": heatmap_data,
            "metric": metric,
            "period": period,
            "legend": {
                "min_value": min([d["metric_value"] for d in heatmap_data]) if heatmap_data else 0,
                "max_value": max([d["metric_value"] for d in heatmap_data]) if heatmap_data else 100,
                "unit": "%" if metric == "turnover" else "score"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get department heatmap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve department heatmap"
        )

# =============================================================================
# OUTLIER DETECTION SYSTEM
# =============================================================================

@router.post("/outliers/detect")
async def detect_outliers(
    method: str = Query("z_score", enum=["z_score", "iqr", "isolation_forest"]),
    threshold: float = Query(2.0, ge=1.0, le=5.0),
    department_id: Optional[uuid.UUID] = None,
    metric_type: str = Query("engagement", enum=["engagement", "performance", "satisfaction", "attendance"]),
    current_user: models.User = Depends(require_roles(["admin", "hr_admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Advanced outlier detection using multiple algorithms"""
    try:
        # Get employees to analyze
        employee_query = db.query(models.Employee).filter(models.Employee.is_active == True)
        if department_id:
            employee_query = employee_query.filter(models.Employee.department_id == department_id)
        
        employees = employee_query.all()
        
        if len(employees) < 3:
            return {
                "outliers": [],
                "message": "Insufficient data for outlier detection (minimum 3 employees required)",
                "method": method,
                "threshold": threshold
            }
        
        # Collect metrics for each employee
        employee_metrics = []
        
        for emp in employees:
            metrics = {}
            
            if metric_type == "engagement":
                # Get latest engagement score
                latest_response = db.query(models.SurveyResponse).filter(
                    models.SurveyResponse.employee_id == emp.id
                ).order_by(desc(models.SurveyResponse.submitted_at)).first()
                
                if latest_response and latest_response.responses.get('engagement_score'):
                    metrics['engagement_score'] = float(latest_response.responses['engagement_score'])
                else:
                    metrics['engagement_score'] = 65.0  # Default/average score
            
            elif metric_type == "performance":
                # Get latest performance review
                latest_review = db.query(models.PerformanceReview).filter(
                    models.PerformanceReview.employee_id == emp.id
                ).order_by(desc(models.PerformanceReview.created_at)).first()
                
                if latest_review:
                    metrics['performance_rating'] = float(latest_review.rating)
                else:
                    metrics['performance_rating'] = 3.0  # Average rating
            
            elif metric_type == "satisfaction":
                # Calculate satisfaction from recent surveys
                satisfaction_scores = db.execute(text("""
                    SELECT AVG(CAST(responses->>'satisfaction_score' AS FLOAT)) as avg_score
                    FROM survey_responses
                    WHERE employee_id = :emp_id
                    AND responses->>'satisfaction_score' IS NOT NULL
                    AND submitted_at >= :start_date
                """), {
                    "emp_id": emp.id,
                    "start_date": datetime.utcnow() - timedelta(days=90)
                }).fetchone()
                
                if satisfaction_scores and satisfaction_scores[0]:
                    metrics['satisfaction_score'] = float(satisfaction_scores[0])
                else:
                    metrics['satisfaction_score'] = 70.0  # Default score
            
            employee_metrics.append({
                "employee_id": emp.id,
                "employee_name": f"{emp.first_name or ''} {emp.last_name or ''}".strip() or emp.name,
                "department_id": emp.department_id,
                "metrics": metrics
            })
        
        # Apply outlier detection algorithm
        outliers = []
        
        if method == "z_score":
            outliers = detect_outliers_z_score(employee_metrics, threshold, metric_type)
        elif method == "iqr":
            outliers = detect_outliers_iqr(employee_metrics, threshold, metric_type)
        elif method == "isolation_forest":
            outliers = detect_outliers_isolation_forest(employee_metrics, metric_type)
        
        # Create outlier records in database
        for outlier in outliers:
            existing_outlier = db.query(models.Outlier).filter(
                and_(
                    models.Outlier.employee_id == outlier["employee_id"],
                    models.Outlier.category == metric_type,
                    models.Outlier.is_resolved == False
                )
            ).first()
            
            if not existing_outlier:
                db_outlier = models.Outlier(
                    employee_id=outlier["employee_id"],
                    type="analytics_based",
                    category=metric_type,
                    severity=outlier["severity"],
                    metrics=outlier["metrics"],
                    contributing_factors=outlier.get("factors", [])
                )
                db.add(db_outlier)
        
        db.commit()
        
        return {
            "outliers": outliers,
            "total_outliers": len(outliers),
            "total_analyzed": len(employee_metrics),
            "outlier_percentage": round(len(outliers) / len(employee_metrics) * 100, 2),
            "method": method,
            "threshold": threshold,
            "metric_type": metric_type,
            "detected_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to detect outliers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect outliers"
        )

@router.get("/outliers/summary")
async def get_outlier_summary(
    department_id: Optional[uuid.UUID] = None,
    severity: Optional[str] = Query(None, enum=["low", "medium", "high", "critical"]),
    resolved: Optional[bool] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get outlier summary and analysis"""
    try:
        # Base query
        query = db.query(models.Outlier)
        
        # Apply filters
        if department_id:
            query = query.join(models.Employee).filter(models.Employee.department_id == department_id)
        if severity:
            query = query.filter(models.Outlier.severity == severity)
        if resolved is not None:
            query = query.filter(models.Outlier.is_resolved == resolved)
        
        outliers = query.all()
        
        # Calculate summary statistics
        total_outliers = len(outliers)
        severity_breakdown = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        category_breakdown = {}
        department_breakdown = {}
        
        for outlier in outliers:
            # Severity breakdown
            if outlier.severity in severity_breakdown:
                severity_breakdown[outlier.severity] += 1
            
            # Category breakdown
            if outlier.category not in category_breakdown:
                category_breakdown[outlier.category] = 0
            category_breakdown[outlier.category] += 1
            
            # Department breakdown
            employee = db.query(models.Employee).filter(models.Employee.id == outlier.employee_id).first()
            if employee and employee.department_id:
                dept = db.query(models.Department).filter(models.Department.id == employee.department_id).first()
                if dept:
                    if dept.name not in department_breakdown:
                        department_breakdown[dept.name] = 0
                    department_breakdown[dept.name] += 1
        
        # Recent outliers (last 7 days)
        recent_outliers = db.query(models.Outlier).filter(
            models.Outlier.identified_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Resolution rate
        resolved_outliers = db.query(models.Outlier).filter(models.Outlier.is_resolved == True).count()
        total_historical = db.query(models.Outlier).count()
        resolution_rate = (resolved_outliers / total_historical * 100) if total_historical > 0 else 0
        
        return {
            "summary": {
                "total_outliers": total_outliers,
                "recent_outliers": recent_outliers,
                "resolution_rate": round(resolution_rate, 2)
            },
            "breakdowns": {
                "by_severity": severity_breakdown,
                "by_category": category_breakdown,
                "by_department": department_breakdown
            },
            "trends": {
                "weekly_detection_rate": recent_outliers,
                "average_resolution_time_days": calculate_average_resolution_time(db)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get outlier summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve outlier summary"
        )

# =============================================================================
# EXPORT FUNCTIONALITY
# =============================================================================

@router.get("/export/dashboard-report")
async def export_dashboard_report(
    format: str = Query("json", enum=["json", "csv", "excel"]),
    department_id: Optional[uuid.UUID] = None,
    period: str = Query("3months", enum=["1month", "3months", "6months", "1year"]),
    current_user: models.User = Depends(require_roles(["admin", "hr_admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Export comprehensive dashboard report"""
    try:
        # Get dashboard data
        overview_data = await get_dashboard_overview(department_id, period, current_user, db)
        
        # Get KPI data
        kpi_data = await get_kpi_trend_charts(None, period, department_id, current_user, db)
        
        # Get outlier data
        outlier_data = await get_outlier_summary(department_id, None, None, current_user, db)
        
        report_data = {
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": current_user.email,
            "period": period,
            "department_filter": str(department_id) if department_id else "All Departments",
            "overview": overview_data,
            "kpi_trends": kpi_data,
            "outlier_analysis": outlier_data
        }
        
        if format == "json":
            return report_data
        elif format == "csv":
            # Convert to CSV format (flattened)
            csv_data = flatten_for_csv(report_data)
            return {"csv_data": csv_data, "filename": f"dashboard_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"}
        elif format == "excel":
            # Return structured data for Excel export
            return {"excel_data": report_data, "filename": f"dashboard_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"}
        
    except Exception as e:
        logger.error(f"Failed to export dashboard report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export dashboard report"
        )

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_trend(values: List[float]) -> float:
    """Calculate trend percentage using linear regression"""
    if len(values) < 2:
        return 0.0
    
    x = list(range(len(values)))
    n = len(values)
    
    # Calculate linear regression slope
    sum_x = sum(x)
    sum_y = sum(values)
    sum_xy = sum(x[i] * values[i] for i in range(n))
    sum_x2 = sum(x[i] ** 2 for i in range(n))
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
    
    # Convert to percentage change
    first_value = values[0]
    if first_value != 0:
        return (slope * (len(values) - 1)) / first_value
    return 0.0

def get_kpi_color(category: str) -> str:
    """Get color for KPI category"""
    colors = {
        "Employee Engagement": "#3B82F6",
        "Turnover Rate": "#EF4444",
        "Training Effectiveness": "#10B981",
        "Diversity Metrics": "#8B5CF6",
        "Performance Metrics": "#F59E0B",
        "Job Satisfaction": "#06B6D4",
        "Employee Wellness": "#84CC16",
        "Productivity Metrics": "#F97316"
    }
    return colors.get(category, "#6B7280")

def get_heatmap_color(intensity: float) -> str:
    """Get heatmap color based on intensity"""
    if intensity <= 0.2:
        return "#FEE2E2"  # Light red
    elif intensity <= 0.4:
        return "#FECACA"  # Light orange
    elif intensity <= 0.6:
        return "#FDE68A"  # Light yellow
    elif intensity <= 0.8:
        return "#BBF7D0"  # Light green
    else:
        return "#86EFAC"  # Green

def detect_outliers_z_score(employee_metrics: List[Dict], threshold: float, metric_type: str) -> List[Dict]:
    """Detect outliers using Z-score method"""
    outliers = []
    
    # Extract values for the specific metric
    values = []
    for emp in employee_metrics:
        if metric_type == "engagement":
            values.append(emp["metrics"].get("engagement_score", 65.0))
        elif metric_type == "performance":
            values.append(emp["metrics"].get("performance_rating", 3.0))
        elif metric_type == "satisfaction":
            values.append(emp["metrics"].get("satisfaction_score", 70.0))
    
    if len(values) < 3:
        return outliers
    
    # Calculate mean and standard deviation
    mean_val = np.mean(values)
    std_val = np.std(values)
    
    if std_val == 0:
        return outliers
    
    # Find outliers
    for i, emp in enumerate(employee_metrics):
        z_score = (values[i] - mean_val) / std_val
        
        if abs(z_score) >= threshold:
            severity = "critical" if abs(z_score) >= 3 else "high" if abs(z_score) >= 2.5 else "medium"
            
            outliers.append({
                "employee_id": emp["employee_id"],
                "employee_name": emp["employee_name"],
                "score": values[i],
                "z_score": round(z_score, 2),
                "deviation_type": "low" if z_score < 0 else "high",
                "severity": severity,
                "metrics": emp["metrics"],
                "factors": [f"Z-score: {round(z_score, 2)}", f"Deviation from mean: {round(values[i] - mean_val, 2)}"]
            })
    
    return outliers

def detect_outliers_iqr(employee_metrics: List[Dict], threshold: float, metric_type: str) -> List[Dict]:
    """Detect outliers using Interquartile Range method"""
    outliers = []
    
    # Extract values
    values = []
    for emp in employee_metrics:
        if metric_type == "engagement":
            values.append(emp["metrics"].get("engagement_score", 65.0))
        elif metric_type == "performance":
            values.append(emp["metrics"].get("performance_rating", 3.0))
        elif metric_type == "satisfaction":
            values.append(emp["metrics"].get("satisfaction_score", 70.0))
    
    if len(values) < 4:
        return outliers
    
    # Calculate IQR
    q1 = np.percentile(values, 25)
    q3 = np.percentile(values, 75)
    iqr = q3 - q1
    
    lower_bound = q1 - (threshold * iqr)
    upper_bound = q3 + (threshold * iqr)
    
    # Find outliers
    for i, emp in enumerate(employee_metrics):
        if values[i] < lower_bound or values[i] > upper_bound:
            severity = "high" if (values[i] < q1 - 3*iqr or values[i] > q3 + 3*iqr) else "medium"
            
            outliers.append({
                "employee_id": emp["employee_id"],
                "employee_name": emp["employee_name"],
                "score": values[i],
                "deviation_type": "low" if values[i] < lower_bound else "high",
                "severity": severity,
                "metrics": emp["metrics"],
                "factors": [f"IQR outlier", f"Value: {values[i]}", f"Range: [{round(lower_bound, 2)}, {round(upper_bound, 2)}]"]
            })
    
    return outliers

def detect_outliers_isolation_forest(employee_metrics: List[Dict], metric_type: str) -> List[Dict]:
    """Detect outliers using Isolation Forest (simplified version)"""
    outliers = []
    
    # For simplicity, use a basic isolation approach
    # In a real implementation, you'd use sklearn.ensemble.IsolationForest
    
    values = []
    for emp in employee_metrics:
        if metric_type == "engagement":
            values.append(emp["metrics"].get("engagement_score", 65.0))
        elif metric_type == "performance":
            values.append(emp["metrics"].get("performance_rating", 3.0))
        elif metric_type == "satisfaction":
            values.append(emp["metrics"].get("satisfaction_score", 70.0))
    
    if len(values) < 5:
        return outliers
    
    # Simple isolation: find values that are very different from the median
    median_val = np.median(values)
    mad = np.median([abs(v - median_val) for v in values])  # Median Absolute Deviation
    
    threshold = 2.5 * mad
    
    for i, emp in enumerate(employee_metrics):
        if abs(values[i] - median_val) > threshold:
            outliers.append({
                "employee_id": emp["employee_id"],
                "employee_name": emp["employee_name"],
                "score": values[i],
                "deviation_type": "low" if values[i] < median_val else "high",
                "severity": "medium",
                "metrics": emp["metrics"],
                "factors": [f"Isolation Forest outlier", f"Deviation from median: {round(abs(values[i] - median_val), 2)}"]
            })
    
    return outliers

def calculate_average_resolution_time(db: Session) -> float:
    """Calculate average resolution time for outliers"""
    resolved_outliers = db.query(models.Outlier).filter(
        and_(
            models.Outlier.is_resolved == True,
            models.Outlier.resolved_at.is_not(None)
        )
    ).all()
    
    if not resolved_outliers:
        return 0.0
    
    total_days = 0
    for outlier in resolved_outliers:
        if outlier.resolved_at and outlier.identified_at:
            delta = outlier.resolved_at - outlier.identified_at
            total_days += delta.days
    
    return total_days / len(resolved_outliers) if resolved_outliers else 0.0

def flatten_for_csv(data: Dict) -> str:
    """Flatten nested dictionary for CSV export"""
    # Simplified CSV conversion
    lines = []
    lines.append("Metric,Value")
    
    def flatten_dict(d, prefix=""):
        for key, value in d.items():
            if isinstance(value, dict):
                flatten_dict(value, f"{prefix}{key}.")
            elif isinstance(value, list):
                lines.append(f"{prefix}{key},{len(value)} items")
            else:
                lines.append(f"{prefix}{key},{value}")
    
    flatten_dict(data)
    return "\\n".join(lines)

# AI-Powered Analytics Endpoints using Cerebras
@router.post("/ai/outlier-analysis")
async def ai_outlier_analysis(
    department_id: Optional[uuid.UUID] = None,
    kpi_thresholds: Optional[Dict[str, Any]] = None,
    current_user: models.User = Depends(require_roles(["admin", "hr_admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Analyze employee outliers using Cerebras AI for deeper insights"""
    try:
        # Get employee data
        employee_query = db.query(models.Employee).join(models.User).filter(
            models.User.is_active == True
        )
        
        if department_id:
            employee_query = employee_query.filter(models.Employee.department_id == department_id)
        elif current_user.role == "manager" and current_user.employee_id:
            employee = db.query(models.Employee).filter(models.Employee.id == current_user.employee_id).first()
            if employee and employee.department_id:
                employee_query = employee_query.filter(models.Employee.department_id == employee.department_id)
        
        employees = employee_query.limit(50).all()  # Limit for AI analysis
        
        # Prepare employee data for AI analysis
        employee_data = []
        for emp in employees:
            # Get recent performance metrics (mock data for demo)
            employee_data.append({
                "id": str(emp.id),
                "name": f"{emp.first_name} {emp.last_name}",
                "role": emp.role,
                "department": emp.department.name if emp.department else "Unknown",
                "hire_date": emp.hire_date.isoformat() if emp.hire_date else None,
                "performance_score": getattr(emp, 'performance_score', 75),
                "engagement_score": getattr(emp, 'engagement_score', 70),
                "satisfaction_score": getattr(emp, 'satisfaction_score', 72),
                "attendance_score": getattr(emp, 'attendance_score', 95)
            })
        
        # Default KPI thresholds if not provided
        if not kpi_thresholds:
            kpi_thresholds = {
                "performance_score": {"min": 60, "max": 100},
                "engagement_score": {"min": 65, "max": 100},
                "satisfaction_score": {"min": 70, "max": 100},
                "attendance_score": {"min": 90, "max": 100}
            }
        
        # Generate AI analysis using Cerebras
        ai_analysis = ai_service.analyze_outliers(
            employee_data=employee_data,
            kpi_thresholds=kpi_thresholds
        )
        
        return {
            "success": True,
            "message": "AI outlier analysis completed",
            "data": {
                "analysis": ai_analysis,
                "employee_count": len(employee_data),
                "department_id": str(department_id) if department_id else None,
                "ai_model": "Cerebras Llama-3.3-70B",
                "analyzed_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"AI outlier analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform AI outlier analysis: {str(e)}"
        )

@router.post("/ai/performance-insights/{employee_id}")
async def get_ai_performance_insights(
    employee_id: uuid.UUID,
    current_user: models.User = Depends(require_roles(["admin", "hr_admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Get AI-powered performance insights for an employee using Cerebras"""
    try:
        # Get employee data
        employee = db.query(models.Employee).join(models.User).filter(
            models.Employee.id == employee_id,
            models.User.is_active == True
        ).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Check if user can access this employee's data
        can_access = (
            current_user.role in ["admin", "hr_admin"] or
            (current_user.role == "manager" and 
             current_user.employee_id and
             employee.department_id == db.query(models.Employee).filter(
                 models.Employee.id == current_user.employee_id
             ).first().department_id)
        )
        
        if not can_access:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Prepare employee data
        employee_data = {
            "id": str(employee.id),
            "name": f"{employee.first_name} {employee.last_name}",
            "role": employee.role,
            "department": employee.department.name if employee.department else "Unknown",
            "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
            "performance_score": getattr(employee, 'performance_score', 75),
            "engagement_score": getattr(employee, 'engagement_score', 70),
            "satisfaction_score": getattr(employee, 'satisfaction_score', 72),
            "attendance_score": getattr(employee, 'attendance_score', 95)
        }
        
        # Mock performance history (in real implementation, this would come from actual data)
        performance_history = [
            {
                "date": (datetime.utcnow() - timedelta(days=90)).isoformat(),
                "performance_score": employee_data["performance_score"] * 0.9,
                "engagement_score": employee_data["engagement_score"] * 0.85,
                "goals_achieved": 3,
                "total_goals": 5
            },
            {
                "date": (datetime.utcnow() - timedelta(days=60)).isoformat(),
                "performance_score": employee_data["performance_score"] * 0.95,
                "engagement_score": employee_data["engagement_score"] * 0.92,
                "goals_achieved": 4,
                "total_goals": 5
            },
            {
                "date": datetime.utcnow().isoformat(),
                "performance_score": employee_data["performance_score"],
                "engagement_score": employee_data["engagement_score"],
                "goals_achieved": 5,
                "total_goals": 5
            }
        ]
        
        # Generate AI insights using Cerebras
        ai_insights = ai_service.generate_performance_insights(
            employee_data=employee_data,
            performance_history=performance_history
        )
        
        return {
            "success": True,
            "message": "AI performance insights generated",
            "data": {
                "employee_id": str(employee_id),
                "employee_name": f"{employee.first_name} {employee.last_name}",
                "insights": ai_insights,
                "ai_model": "Cerebras Llama-3.3-70B",
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI performance insights failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI performance insights: {str(e)}"
        )

@router.post("/ai/analyze-outliers")
async def analyze_outliers_with_ai(
    employee_data: List[Dict[str, Any]],
    kpi_thresholds: Dict[str, Any],
    current_user: models.User = Depends(require_roles(["admin", "hr_admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Analyze outliers using AI - matches frontend API call"""
    try:
        # Generate AI analysis using Cerebras
        ai_analysis = ai_service.analyze_outliers(
            employee_data=employee_data,
            kpi_thresholds=kpi_thresholds
        )
        
        return {
            "success": True,
            "message": "AI outlier analysis completed",
            "data": ai_analysis,
            "ai_model": "Cerebras Llama-3.3-70B",
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AI outlier analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform AI outlier analysis: {str(e)}"
        )

@router.post("/ai/analyze-sentiment")
async def analyze_sentiment_analytics(
    text_list: List[str],
    current_user: models.User = Depends(require_roles(["admin", "hr_admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Analyze sentiment using AI - matches frontend API call"""
    try:
        # Analyze sentiment using AI service
        sentiment_analysis = ai_service.analyze_sentiment(text_list)
        
        return {
            "success": True,
            "message": "Sentiment analysis completed successfully",
            "data": sentiment_analysis,
            "ai_model": "Cerebras Llama-3.3-70B",
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze sentiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze sentiment: {str(e)}"
        )