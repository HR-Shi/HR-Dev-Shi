from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any
import models
import schemas
from database import get_db
from auth.dependencies import get_current_active_user, require_roles
import logging
from datetime import datetime, timedelta
import uuid
from enum import Enum

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/kpis",
    tags=["KPIs"]
)

# Predefined KPI Categories and Options
class KPICategory(str, Enum):
    ENGAGEMENT = "Employee Engagement"
    TURNOVER = "Turnover Rate"
    TRAINING = "Training Effectiveness"
    DIVERSITY = "Diversity Metrics"
    PERFORMANCE = "Performance Metrics"
    SATISFACTION = "Job Satisfaction"
    WELLNESS = "Employee Wellness"
    PRODUCTIVITY = "Productivity Metrics"

PREDEFINED_KPIS = {
    KPICategory.ENGAGEMENT: [
        {
            "name": "Overall Employee Engagement Score",
            "description": "Measures overall employee engagement based on surveys",
            "measurement_type": "percentage",
            "default_target": 75.0,
            "frequency": "monthly",
            "calculation_method": "average_score"
        },
        {
            "name": "Employee Net Promoter Score (eNPS)",
            "description": "Measures likelihood of employees recommending company as workplace",
            "measurement_type": "score",
            "default_target": 50.0,
            "frequency": "quarterly",
            "calculation_method": "nps_formula"
        },
        {
            "name": "Engagement Survey Participation Rate",
            "description": "Percentage of employees participating in engagement surveys",
            "measurement_type": "percentage",
            "default_target": 85.0,
            "frequency": "monthly",
            "calculation_method": "participation_rate"
        }
    ],
    KPICategory.TURNOVER: [
        {
            "name": "Overall Turnover Rate",
            "description": "Percentage of employees leaving the organization",
            "measurement_type": "percentage",
            "default_target": 10.0,
            "frequency": "monthly",
            "calculation_method": "turnover_rate"
        },
        {
            "name": "Voluntary Turnover Rate",
            "description": "Percentage of employees voluntarily leaving the organization",
            "measurement_type": "percentage",
            "default_target": 8.0,
            "frequency": "monthly",
            "calculation_method": "voluntary_turnover"
        },
        {
            "name": "High Performer Retention Rate",
            "description": "Percentage of high performers retained",
            "measurement_type": "percentage",
            "default_target": 95.0,
            "frequency": "quarterly",
            "calculation_method": "retention_rate"
        }
    ],
    KPICategory.TRAINING: [
        {
            "name": "Training Completion Rate",
            "description": "Percentage of assigned training completed on time",
            "measurement_type": "percentage",
            "default_target": 90.0,
            "frequency": "monthly",
            "calculation_method": "completion_rate"
        },
        {
            "name": "Training Effectiveness Score",
            "description": "Measures effectiveness of training programs",
            "measurement_type": "score",
            "default_target": 4.0,
            "frequency": "quarterly",
            "calculation_method": "average_rating"
        },
        {
            "name": "Skill Development Progress",
            "description": "Measures improvement in key skills",
            "measurement_type": "percentage",
            "default_target": 20.0,
            "frequency": "quarterly",
            "calculation_method": "skill_improvement"
        }
    ],
    KPICategory.DIVERSITY: [
        {
            "name": "Gender Diversity Ratio",
            "description": "Gender balance across the organization",
            "measurement_type": "ratio",
            "default_target": 50.0,
            "frequency": "quarterly",
            "calculation_method": "diversity_ratio"
        },
        {
            "name": "Leadership Diversity",
            "description": "Diversity in leadership positions",
            "measurement_type": "percentage",
            "default_target": 40.0,
            "frequency": "quarterly",
            "calculation_method": "leadership_diversity"
        },
        {
            "name": "Inclusion Index",
            "description": "Measures sense of inclusion across diverse groups",
            "measurement_type": "score",
            "default_target": 4.2,
            "frequency": "quarterly",
            "calculation_method": "inclusion_score"
        }
    ]
}

@router.get("/predefined")
async def get_predefined_kpis(
    category: Optional[KPICategory] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get predefined KPI options"""
    try:
        if category:
            return {
                "category": category,
                "kpis": PREDEFINED_KPIS.get(category, [])
            }
        
        return {
            "categories": list(KPICategory),
            "all_kpis": PREDEFINED_KPIS
        }
        
    except Exception as e:
        logger.error(f"Failed to get predefined KPIs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve predefined KPIs"
        )

@router.get("/", response_model=List[schemas.KPI])
async def get_kpis(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    is_active: Optional[bool] = True,
    department_id: Optional[uuid.UUID] = None,
    priority: Optional[str] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get KPIs with filtering options"""
    try:
        query = db.query(models.KPI)
        
        # Apply filters based on user role
        if current_user.role == "manager":
            # Managers can only see KPIs for their department
            if current_user.employee_id:
                employee = db.query(models.Employee).filter(models.Employee.id == current_user.employee_id).first()
                if employee and employee.department_id:
                    query = query.filter(
                        or_(
                            models.KPI.department_id == employee.department_id,
                            models.KPI.department_id.is_(None)  # Organization-wide KPIs
                        )
                    )
        
        if category:
            query = query.filter(models.KPI.category == category)
        if is_active is not None:
            query = query.filter(models.KPI.is_active == is_active)
        if department_id:
            query = query.filter(models.KPI.department_id == department_id)
        if priority:
            query = query.filter(models.KPI.priority == priority)
        
        # Order by priority and creation date
        query = query.order_by(
            func.case(
                (models.KPI.priority == "high", 1),
                (models.KPI.priority == "medium", 2),
                (models.KPI.priority == "low", 3),
                else_=4
            ),
            desc(models.KPI.created_at)
        )
        
        kpis = query.offset(skip).limit(limit).all()
        return kpis
        
    except Exception as e:
        logger.error(f"Failed to get KPIs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve KPIs"
        )

@router.post("/", response_model=schemas.KPI)
async def create_kpi(
    kpi: schemas.KPICreate,
    current_user: models.User = Depends(require_roles(["admin", "hr_admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Create a new KPI"""
    try:
        # Validate department access for managers
        if current_user.role == "manager" and kpi.department_id:
            if current_user.employee_id:
                employee = db.query(models.Employee).filter(models.Employee.id == current_user.employee_id).first()
                if not employee or employee.department_id != kpi.department_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Cannot create KPI for different department"
                    )
        
        # Create KPI
        db_kpi = models.KPI(
            name=kpi.name,
            description=kpi.description,
            category=kpi.category,
            measurement_type=kpi.measurement_type,
            target_value=kpi.target_value,
            measurement_frequency=kpi.measurement_frequency,
            calculation_method=kpi.calculation_method,
            department_id=kpi.department_id,
            priority=kpi.priority or "medium",
            is_active=True,
            created_by=current_user.id
        )
        
        db.add(db_kpi)
        db.commit()
        db.refresh(db_kpi)
        
        logger.info(f"KPI created by {current_user.email}: {kpi.name}")
        return db_kpi
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create KPI: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create KPI"
        )

@router.get("/{kpi_id}", response_model=schemas.KPI)
async def get_kpi(
    kpi_id: uuid.UUID,
    include_measurements: bool = Query(False),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get KPI by ID with optional measurements"""
    try:
        kpi = db.query(models.KPI).filter(models.KPI.id == kpi_id).first()
        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPI not found"
            )
        
        # Check access permissions
        if current_user.role == "manager":
            if current_user.employee_id:
                employee = db.query(models.Employee).filter(models.Employee.id == current_user.employee_id).first()
                if employee and kpi.department_id and employee.department_id != kpi.department_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied to this KPI"
                    )
        
        if include_measurements:
            # Get recent measurements
            measurements = db.query(models.KPIMeasurement).filter(
                models.KPIMeasurement.kpi_id == kpi_id
            ).order_by(desc(models.KPIMeasurement.measurement_date)).limit(10).all()
            
            kpi_dict = kpi.__dict__.copy()
            kpi_dict['recent_measurements'] = measurements
            return kpi_dict
        
        return kpi
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get KPI {kpi_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve KPI"
        )

@router.put("/{kpi_id}", response_model=schemas.KPI)
async def update_kpi(
    kpi_id: uuid.UUID,
    kpi_update: schemas.KPIUpdate,
    current_user: models.User = Depends(require_roles(["admin", "hr_admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Update KPI"""
    try:
        kpi = db.query(models.KPI).filter(models.KPI.id == kpi_id).first()
        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPI not found"
            )
        
        # Check permissions
        if current_user.role == "manager":
            if current_user.employee_id:
                employee = db.query(models.Employee).filter(models.Employee.id == current_user.employee_id).first()
                if employee and kpi.department_id and employee.department_id != kpi.department_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Cannot update KPI for different department"
                    )
        
        # Update fields
        for field, value in kpi_update.dict(exclude_unset=True).items():
            setattr(kpi, field, value)
        
        kpi.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(kpi)
        
        logger.info(f"KPI updated by {current_user.email}: {kpi.name}")
        return kpi
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update KPI {kpi_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update KPI"
        )

@router.post("/{kpi_id}/measurements")
async def add_kpi_measurement(
    kpi_id: uuid.UUID,
    measurement: schemas.KPIMeasurementCreate,
    current_user: models.User = Depends(require_roles(["admin", "hr_admin", "manager"])),
    db: Session = Depends(get_db)
):
    """Add a measurement to a KPI"""
    try:
        kpi = db.query(models.KPI).filter(models.KPI.id == kpi_id).first()
        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPI not found"
            )
        
        # Create measurement
        db_measurement = models.KPIMeasurement(
            kpi_id=kpi_id,
            value=measurement.value,
            measurement_date=measurement.measurement_date or datetime.utcnow(),
            notes=measurement.notes,
            recorded_by=current_user.id
        )
        
        db.add(db_measurement)
        
        # Update KPI current value and last measurement date
        kpi.current_value = measurement.value
        kpi.last_measured_at = db_measurement.measurement_date
        kpi.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_measurement)
        
        logger.info(f"KPI measurement added by {current_user.email} for {kpi.name}: {measurement.value}")
        return db_measurement
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add measurement to KPI {kpi_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add KPI measurement"
        )

@router.get("/{kpi_id}/measurements")
async def get_kpi_measurements(
    kpi_id: uuid.UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(50, ge=1, le=1000),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get measurements for a KPI"""
    try:
        kpi = db.query(models.KPI).filter(models.KPI.id == kpi_id).first()
        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPI not found"
            )
        
        query = db.query(models.KPIMeasurement).filter(models.KPIMeasurement.kpi_id == kpi_id)
        
        if start_date:
            query = query.filter(models.KPIMeasurement.measurement_date >= start_date)
        if end_date:
            query = query.filter(models.KPIMeasurement.measurement_date <= end_date)
        
        measurements = query.order_by(desc(models.KPIMeasurement.measurement_date)).limit(limit).all()
        
        return {
            "kpi_id": kpi_id,
            "kpi_name": kpi.name,
            "target_value": kpi.target_value,
            "measurements": measurements,
            "measurement_count": len(measurements)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get measurements for KPI {kpi_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve KPI measurements"
        )

@router.get("/{kpi_id}/analytics")
async def get_kpi_analytics(
    kpi_id: uuid.UUID,
    period: str = Query("3months", enum=["1month", "3months", "6months", "1year"]),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics for a KPI"""
    try:
        kpi = db.query(models.KPI).filter(models.KPI.id == kpi_id).first()
        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPI not found"
            )
        
        # Calculate date range
        period_days = {
            "1month": 30,
            "3months": 90,
            "6months": 180,
            "1year": 365
        }
        
        start_date = datetime.utcnow() - timedelta(days=period_days[period])
        
        # Get measurements in period
        measurements = db.query(models.KPIMeasurement).filter(
            and_(
                models.KPIMeasurement.kpi_id == kpi_id,
                models.KPIMeasurement.measurement_date >= start_date
            )
        ).order_by(models.KPIMeasurement.measurement_date).all()
        
        if not measurements:
            return {
                "kpi": {"id": kpi.id, "name": kpi.name, "target_value": kpi.target_value},
                "period": period,
                "analytics": {
                    "message": "No measurements found for the specified period"
                }
            }
        
        values = [m.value for m in measurements]
        
        # Calculate analytics
        current_value = values[-1] if values else None
        average_value = sum(values) / len(values) if values else 0
        min_value = min(values) if values else None
        max_value = max(values) if values else None
        
        # Calculate trend
        if len(values) >= 2:
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            trend = "improving" if second_avg > first_avg else "declining" if second_avg < first_avg else "stable"
            trend_percentage = ((second_avg - first_avg) / first_avg * 100) if first_avg != 0 else 0
        else:
            trend = "insufficient_data"
            trend_percentage = 0
        
        # Target achievement
        target_achievement = None
        on_target = None
        if kpi.target_value and current_value is not None:
            target_achievement = (current_value / kpi.target_value) * 100
            on_target = abs(current_value - kpi.target_value) <= (kpi.target_value * 0.05)  # Within 5%
        
        # Variance analysis
        variance = None
        if len(values) > 1:
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        return {
            "kpi": {
                "id": kpi.id,
                "name": kpi.name,
                "category": kpi.category,
                "target_value": kpi.target_value,
                "measurement_type": kpi.measurement_type
            },
            "period": period,
            "analytics": {
                "current_value": current_value,
                "average_value": round(average_value, 2),
                "min_value": min_value,
                "max_value": max_value,
                "trend": trend,
                "trend_percentage": round(trend_percentage, 2),
                "target_achievement_percentage": round(target_achievement, 2) if target_achievement else None,
                "on_target": on_target,
                "variance": round(variance, 2) if variance else None,
                "measurement_count": len(measurements),
                "measurement_frequency": kpi.measurement_frequency
            },
            "measurements": [
                {
                    "date": m.measurement_date.isoformat(),
                    "value": m.value,
                    "notes": m.notes
                }
                for m in measurements
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analytics for KPI {kpi_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve KPI analytics"
        )

@router.get("/dashboard/summary")
async def get_kpi_dashboard_summary(
    department_id: Optional[uuid.UUID] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get KPI dashboard summary with key metrics"""
    try:
        query = db.query(models.KPI).filter(models.KPI.is_active == True)
        
        # Apply department filter based on user role
        if current_user.role == "manager":
            if current_user.employee_id:
                employee = db.query(models.Employee).filter(models.Employee.id == current_user.employee_id).first()
                if employee and employee.department_id:
                    query = query.filter(
                        or_(
                            models.KPI.department_id == employee.department_id,
                            models.KPI.department_id.is_(None)
                        )
                    )
        elif department_id:
            query = query.filter(models.KPI.department_id == department_id)
        
        kpis = query.all()
        
        # Calculate summary metrics
        total_kpis = len(kpis)
        kpis_with_targets = len([k for k in kpis if k.target_value is not None])
        kpis_on_target = 0
        kpis_off_target = 0
        kpis_without_data = 0
        
        category_breakdown = {}
        priority_breakdown = {"high": 0, "medium": 0, "low": 0}
        
        for kpi in kpis:
            # Category breakdown
            if kpi.category not in category_breakdown:
                category_breakdown[kpi.category] = 0
            category_breakdown[kpi.category] += 1
            
            # Priority breakdown
            if kpi.priority in priority_breakdown:
                priority_breakdown[kpi.priority] += 1
            
            # Target achievement analysis
            if kpi.current_value is not None and kpi.target_value is not None:
                # Within 5% of target is considered "on target"
                if abs(kpi.current_value - kpi.target_value) <= (kpi.target_value * 0.05):
                    kpis_on_target += 1
                else:
                    kpis_off_target += 1
            elif kpi.target_value is not None:
                kpis_without_data += 1
        
        # Get recent alerts (KPIs significantly off target)
        alerts = []
        for kpi in kpis:
            if kpi.current_value is not None and kpi.target_value is not None:
                deviation = abs(kpi.current_value - kpi.target_value) / kpi.target_value * 100
                if deviation > 20:  # More than 20% off target
                    alerts.append({
                        "kpi_id": kpi.id,
                        "kpi_name": kpi.name,
                        "current_value": kpi.current_value,
                        "target_value": kpi.target_value,
                        "deviation_percentage": round(deviation, 2),
                        "priority": kpi.priority,
                        "last_measured": kpi.last_measured_at
                    })
        
        # Sort alerts by deviation
        alerts.sort(key=lambda x: x["deviation_percentage"], reverse=True)
        
        return {
            "summary": {
                "total_kpis": total_kpis,
                "kpis_with_targets": kpis_with_targets,
                "kpis_on_target": kpis_on_target,
                "kpis_off_target": kpis_off_target,
                "kpis_without_data": kpis_without_data,
                "target_achievement_rate": round((kpis_on_target / kpis_with_targets * 100), 2) if kpis_with_targets > 0 else 0
            },
            "breakdowns": {
                "by_category": category_breakdown,
                "by_priority": priority_breakdown
            },
            "alerts": alerts[:10],  # Top 10 alerts
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get KPI dashboard summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve KPI dashboard summary"
        )

@router.post("/bulk/prioritize")
async def bulk_prioritize_kpis(
    kpi_priorities: List[Dict[str, str]],  # [{"kpi_id": "...", "priority": "high/medium/low"}]
    current_user: models.User = Depends(require_roles(["admin", "hr_admin"])),
    db: Session = Depends(get_db)
):
    """Bulk update KPI priorities"""
    try:
        updated_count = 0
        failed_updates = []
        
        for update in kpi_priorities:
            try:
                kpi_id = update.get("kpi_id")
                priority = update.get("priority")
                
                if not kpi_id or priority not in ["high", "medium", "low"]:
                    failed_updates.append({"kpi_id": kpi_id, "error": "Invalid kpi_id or priority"})
                    continue
                
                kpi = db.query(models.KPI).filter(models.KPI.id == kpi_id).first()
                if not kpi:
                    failed_updates.append({"kpi_id": kpi_id, "error": "KPI not found"})
                    continue
                
                kpi.priority = priority
                kpi.updated_at = datetime.utcnow()
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to update priority for KPI {kpi_id}: {e}")
                failed_updates.append({"kpi_id": kpi_id, "error": str(e)})
        
        db.commit()
        
        logger.info(f"Bulk KPI prioritization by {current_user.email}: {updated_count} KPIs updated")
        
        return {
            "message": f"Successfully updated {updated_count} KPI priorities",
            "updated_count": updated_count,
            "failed_updates": failed_updates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed bulk KPI prioritization: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update KPI priorities"
        ) 