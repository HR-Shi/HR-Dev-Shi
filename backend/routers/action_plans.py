from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid

from database import get_db
from models import (
    ActionPlanTemplate, ActionPlan, ActionPlanProgress, 
    FocusGroup, Employee, Department, User, KPI
)
from schemas import (
    ActionPlanTemplateCreate, ActionPlanTemplateUpdate, ActionPlanTemplateResponse,
    ActionPlanCreate, ActionPlanUpdate, ActionPlanResponse, ActionPlanList,
    ActionPlanMilestoneCreate, ActionPlanMilestoneUpdate, ActionPlanMilestoneResponse,
    ActionPlanProgressUpdate, ActionPlanAnalytics
)
from auth.dependencies import get_current_user, require_roles
from ai_service import ai_service

router = APIRouter(prefix="/action-plans", tags=["action-plans"])

# Action Plan Templates
@router.get("/templates", response_model=List[ActionPlanTemplateResponse])
async def list_action_plan_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all action plan templates with filtering options"""
    query = select(ActionPlanTemplate)
    
    if category:
        query = query.where(ActionPlanTemplate.category == category)
    if is_active is not None:
        query = query.where(ActionPlanTemplate.is_active == is_active)
    
    query = query.offset(skip).limit(limit).order_by(ActionPlanTemplate.created_at.desc())
    
    result = await db.execute(query)
    templates = result.scalars().all()
    
    return templates

@router.post("/templates", response_model=ActionPlanTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_action_plan_template(
    template: ActionPlanTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hr_admin"]))
):
    """Create a new action plan template"""
    db_template = ActionPlanTemplate(
        **template.dict(),
        created_by=current_user.id
    )
    
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)
    
    return db_template

@router.get("/templates/{template_id}", response_model=ActionPlanTemplateResponse)
async def get_action_plan_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific action plan template"""
    result = await db.execute(
        select(ActionPlanTemplate).where(ActionPlanTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action plan template not found"
        )
    
    return template

@router.put("/templates/{template_id}", response_model=ActionPlanTemplateResponse)
async def update_action_plan_template(
    template_id: uuid.UUID,
    template_update: ActionPlanTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hr_admin"]))
):
    """Update an action plan template"""
    result = await db.execute(
        select(ActionPlanTemplate).where(ActionPlanTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action plan template not found"
        )
    
    update_data = template_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    template.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(template)
    
    return template

@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action_plan_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hr_admin"]))
):
    """Delete an action plan template"""
    result = await db.execute(
        select(ActionPlanTemplate).where(ActionPlanTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action plan template not found"
        )
    
    await db.execute(
        delete(ActionPlanTemplate).where(ActionPlanTemplate.id == template_id)
    )
    await db.commit()

# Action Plans
@router.get("", response_model=ActionPlanList)
async def list_action_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = None,
    department_id: Optional[uuid.UUID] = None,
    focus_group_id: Optional[uuid.UUID] = None,
    assigned_to: Optional[uuid.UUID] = None,
    created_by: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List action plans with filtering and pagination"""
    query = select(ActionPlan)
    count_query = select(func.count(ActionPlan.id))
    
    # Apply filters
    filters = []
    if status_filter:
        filters.append(ActionPlan.status == status_filter)
    if department_id:
        filters.append(ActionPlan.department_id == department_id)
    if focus_group_id:
        filters.append(ActionPlan.focus_group_id == focus_group_id)
    if assigned_to:
        filters.append(ActionPlan.assigned_to == assigned_to)
    if created_by:
        filters.append(ActionPlan.created_by == created_by)
    
    # Apply role-based filtering
    if current_user.role not in ["admin", "hr_admin"]:
        if current_user.role == "manager":
            # Managers can see plans for their department
            filters.append(ActionPlan.department_id == current_user.department_id)
        else:
            # Employees can only see plans assigned to them
            filters.append(ActionPlan.assigned_to == current_user.id)
    
    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(ActionPlan.created_at.desc())
    result = await db.execute(query)
    action_plans = result.scalars().all()
    
    return ActionPlanList(
        items=action_plans,
        total=total,
        skip=skip,
        limit=limit
    )

@router.post("", response_model=ActionPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_action_plan(
    action_plan: ActionPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hr_admin", "manager"]))
):
    """Create a new action plan"""
    # Validate foreign key relationships
    if action_plan.template_id:
        template_result = await db.execute(
            select(ActionPlanTemplate).where(ActionPlanTemplate.id == action_plan.template_id)
        )
        if not template_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid template_id"
            )
    
    if action_plan.focus_group_id:
        focus_group_result = await db.execute(
            select(FocusGroup).where(FocusGroup.id == action_plan.focus_group_id)
        )
        if not focus_group_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid focus_group_id"
            )
    
    if action_plan.assigned_to:
        user_result = await db.execute(
            select(User).where(User.id == action_plan.assigned_to)
        )
        if not user_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid assigned_to user_id"
            )
    
    db_action_plan = ActionPlan(
        **action_plan.dict(),
        created_by=current_user.id,
        status="draft"
    )
    
    db.add(db_action_plan)
    await db.commit()
    await db.refresh(db_action_plan)
    
    return db_action_plan

@router.get("/{action_plan_id}", response_model=ActionPlanResponse)
async def get_action_plan(
    action_plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific action plan"""
    result = await db.execute(
        select(ActionPlan).where(ActionPlan.id == action_plan_id)
    )
    action_plan = result.scalar_one_or_none()
    
    if not action_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action plan not found"
        )
    
    # Check permissions
    if current_user.role not in ["admin", "hr_admin"]:
        if current_user.role == "manager":
            if action_plan.department_id != current_user.department_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        else:
            if action_plan.assigned_to != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
    
    return action_plan

@router.put("/{action_plan_id}", response_model=ActionPlanResponse)
async def update_action_plan(
    action_plan_id: uuid.UUID,
    action_plan_update: ActionPlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an action plan"""
    result = await db.execute(
        select(ActionPlan).where(ActionPlan.id == action_plan_id)
    )
    action_plan = result.scalar_one_or_none()
    
    if not action_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action plan not found"
        )
    
    # Check permissions
    can_edit = (
        current_user.role in ["admin", "hr_admin"] or
        action_plan.created_by == current_user.id or
        action_plan.assigned_to == current_user.id or
        (current_user.role == "manager" and action_plan.department_id == current_user.department_id)
    )
    
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    update_data = action_plan_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(action_plan, field, value)
    
    action_plan.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(action_plan)
    
    return action_plan

@router.delete("/{action_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action_plan(
    action_plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hr_admin"]))
):
    """Delete an action plan"""
    result = await db.execute(
        select(ActionPlan).where(ActionPlan.id == action_plan_id)
    )
    action_plan = result.scalar_one_or_none()
    
    if not action_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action plan not found"
        )
    
    await db.execute(
        delete(ActionPlan).where(ActionPlan.id == action_plan_id)
    )
    await db.commit()

# Action Plan Progress & Status Updates
@router.put("/{action_plan_id}/progress", response_model=ActionPlanResponse)
async def update_action_plan_progress(
    action_plan_id: uuid.UUID,
    progress_update: ActionPlanProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update action plan progress and status"""
    result = await db.execute(
        select(ActionPlan).where(ActionPlan.id == action_plan_id)
    )
    action_plan = result.scalar_one_or_none()
    
    if not action_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action plan not found"
        )
    
    # Check permissions
    can_update = (
        current_user.role in ["admin", "hr_admin"] or
        action_plan.assigned_to == current_user.id or
        (current_user.role == "manager" and action_plan.department_id == current_user.department_id)
    )
    
    if not can_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update progress
    if progress_update.progress_percentage is not None:
        action_plan.progress_percentage = progress_update.progress_percentage
    
    if progress_update.status:
        action_plan.status = progress_update.status
    
    if progress_update.notes:
        action_plan.notes = progress_update.notes
    
    # Auto-update status based on progress
    if action_plan.progress_percentage == 100 and action_plan.status != "completed":
        action_plan.status = "completed"
        action_plan.completed_at = datetime.utcnow()
    elif action_plan.progress_percentage > 0 and action_plan.status == "draft":
        action_plan.status = "in_progress"
    
    action_plan.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(action_plan)
    
    return action_plan

# Milestones
@router.get("/{action_plan_id}/milestones", response_model=List[Dict[str, Any]])
async def list_action_plan_milestones(
    action_plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List milestones for an action plan"""
    # Verify action plan exists and user has access
    action_plan = await get_action_plan(action_plan_id, db, current_user)
    
    # Return milestones from JSON column
    return action_plan.milestones or []

@router.post("/{action_plan_id}/milestones", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_action_plan_milestone(
    action_plan_id: uuid.UUID,
    milestone: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a milestone for an action plan"""
    # Verify action plan exists and user has access
    action_plan = await get_action_plan(action_plan_id, db, current_user)
    
    # Check if user can edit this action plan
    can_edit = (
        current_user.role in ["admin", "hr_admin"] or
        action_plan.created_by == current_user.id or
        action_plan.assigned_to == current_user.id
    )
    
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Add milestone to JSON array
    milestones = action_plan.milestones or []
    milestone_with_id = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat(),
        **milestone
    }
    milestones.append(milestone_with_id)
    
    action_plan.milestones = milestones
    action_plan.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(action_plan)
    
    return milestone_with_id

@router.put("/milestones/{milestone_id}", response_model=Dict[str, Any])
async def update_action_plan_milestone(
    milestone_id: str,
    milestone_update: Dict[str, Any],
    action_plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a milestone"""
    # Get the action plan
    action_plan = await get_action_plan(action_plan_id, db, current_user)
    
    can_edit = (
        current_user.role in ["admin", "hr_admin"] or
        action_plan.created_by == current_user.id or
        action_plan.assigned_to == current_user.id
    )
    
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Find and update milestone in JSON array
    milestones = action_plan.milestones or []
    milestone_found = False
    
    for i, milestone in enumerate(milestones):
        if milestone.get("id") == milestone_id:
            milestones[i] = {**milestone, **milestone_update, "updated_at": datetime.utcnow().isoformat()}
            milestone_found = True
            break
    
    if not milestone_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    
    action_plan.milestones = milestones
    action_plan.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(action_plan)
    
    return milestones[i]

@router.delete("/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action_plan_milestone(
    milestone_id: str,
    action_plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a milestone"""
    # Get the action plan
    action_plan = await get_action_plan(action_plan_id, db, current_user)
    
    can_edit = (
        current_user.role in ["admin", "hr_admin"] or
        action_plan.created_by == current_user.id or
        action_plan.assigned_to == current_user.id
    )
    
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Remove milestone from JSON array
    milestones = action_plan.milestones or []
    original_length = len(milestones)
    milestones = [m for m in milestones if m.get("id") != milestone_id]
    
    if len(milestones) == original_length:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    
    action_plan.milestones = milestones
    action_plan.updated_at = datetime.utcnow()
    
    await db.commit()

# Analytics
@router.get("/stats/summary", response_model=ActionPlanAnalytics)
async def get_action_plan_analytics(
    department_id: Optional[uuid.UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hr_admin", "manager"]))
):
    """Get action plan analytics and statistics"""
    query = select(ActionPlan)
    
    # Apply filters
    filters = []
    if department_id:
        filters.append(ActionPlan.department_id == department_id)
    if date_from:
        filters.append(ActionPlan.created_at >= date_from)
    if date_to:
        filters.append(ActionPlan.created_at <= date_to)
    
    # Apply role-based filtering
    if current_user.role == "manager":
        filters.append(ActionPlan.department_id == current_user.department_id)
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    action_plans = result.scalars().all()
    
    # Calculate statistics
    total_plans = len(action_plans)
    completed_plans = len([ap for ap in action_plans if ap.status == "completed"])
    in_progress_plans = len([ap for ap in action_plans if ap.status == "in_progress"])
    draft_plans = len([ap for ap in action_plans if ap.status == "draft"])
    overdue_plans = len([
        ap for ap in action_plans 
        if ap.due_date and ap.due_date < datetime.utcnow().date() and ap.status != "completed"
    ])
    
    avg_progress = sum([ap.progress_percentage or 0 for ap in action_plans]) / total_plans if total_plans > 0 else 0
    
    # Status distribution
    status_distribution = {
        "draft": draft_plans,
        "in_progress": in_progress_plans,
        "completed": completed_plans,
        "overdue": overdue_plans
    }
    
    # Completion rate
    completion_rate = (completed_plans / total_plans * 100) if total_plans > 0 else 0
    
    return ActionPlanAnalytics(
        total_plans=total_plans,
        completed_plans=completed_plans,
        in_progress_plans=in_progress_plans,
        draft_plans=draft_plans,
        overdue_plans=overdue_plans,
        average_progress=round(avg_progress, 2),
        completion_rate=round(completion_rate, 2),
        status_distribution=status_distribution
    )

# AI-Powered Endpoints using Cerebras
@router.post("/ai/generate-recommendations")
async def generate_ai_action_plan_recommendations(
    issue_type: str,
    department_id: Optional[uuid.UUID] = None,
    focus_group_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hr_admin", "manager"]))
):
    """Generate AI-powered action plan recommendations using Cerebras"""
    try:
        # Gather relevant KPI data
        kpi_query = select(KPI).where(KPI.is_active == True)
        if department_id:
            kpi_query = kpi_query.where(KPI.department_id == department_id)
        
        kpi_result = await db.execute(kpi_query)
        kpis = kpi_result.scalars().all()
        
        kpi_data = {
            "department_kpis": [
                {
                    "name": kpi.name,
                    "current_value": kpi.current_value,
                    "target_value": kpi.target_value,
                    "trend": kpi.trend
                }
                for kpi in kpis
            ]
        }
        
        # Gather employee data for context
        employee_query = select(Employee).join(User).where(User.is_active == True)
        if department_id:
            employee_query = employee_query.where(Employee.department_id == department_id)
        
        employee_query = employee_query.limit(10)  # Sample for AI analysis
        employee_result = await db.execute(employee_query)
        employees = employee_result.scalars().all()
        
        employee_data = [
            {
                "id": str(emp.id),
                "role": emp.role,
                "performance_score": getattr(emp, 'performance_score', 75),
                "engagement_score": getattr(emp, 'engagement_score', 70)
            }
            for emp in employees
        ]
        
        # Generate AI recommendations using Cerebras
        ai_recommendations = ai_service.generate_action_plan_templates(
            issue_type=issue_type,
            kpi_data=kpi_data,
            employee_data=employee_data
        )
        
        return {
            "success": True,
            "message": "AI action plan recommendations generated successfully",
            "data": {
                "issue_type": issue_type,
                "department_id": str(department_id) if department_id else None,
                "ai_recommendations": ai_recommendations,
                "context": {
                    "kpis_analyzed": len(kpis),
                    "employees_analyzed": len(employees)
                },
                "ai_model": "Cerebras Llama-3.3-70B",
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI recommendations: {str(e)}"
        )

@router.post("/ai/analyze-efficacy/{action_plan_id}")
async def analyze_action_plan_efficacy(
    action_plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hr_admin", "manager"]))
):
    """Analyze action plan efficacy using Cerebras AI"""
    try:
        # Get the action plan
        action_plan = await get_action_plan(action_plan_id, db, current_user)
        
        # Get related KPIs before and after implementation
        if action_plan.department_id:
            kpi_result = await db.execute(
                select(KPI).where(
                    and_(
                        KPI.department_id == action_plan.department_id,
                        KPI.is_active == True
                    )
                )
            )
            kpis = kpi_result.scalars().all()
        else:
            kpis = []
        
        # Prepare data for AI analysis
        action_plan_data = {
            "title": action_plan.title,
            "description": action_plan.description,
            "status": action_plan.status,
            "progress": action_plan.progress_percentage,
            "start_date": action_plan.start_date.isoformat() if action_plan.start_date else None,
            "due_date": action_plan.due_date.isoformat() if action_plan.due_date else None,
            "milestones": action_plan.milestones or []
        }
        
        # Mock before/after metrics (in real implementation, you'd track these over time)
        before_metrics = {
            kpi.name: {
                "value": kpi.current_value * 0.9,  # Simulate 10% worse before
                "target": kpi.target_value
            }
            for kpi in kpis
        }
        
        after_metrics = {
            kpi.name: {
                "value": kpi.current_value,
                "target": kpi.target_value
            }
            for kpi in kpis
        }
        
        # Generate AI efficacy analysis using Cerebras
        efficacy_analysis = ai_service.analyze_action_plan_efficacy(
            action_plan_data=action_plan_data,
            before_metrics=before_metrics,
            after_metrics=after_metrics
        )
        
        return {
            "success": True,
            "message": "Action plan efficacy analysis completed",
            "data": {
                "action_plan_id": str(action_plan_id),
                "efficacy_analysis": efficacy_analysis,
                "ai_model": "Cerebras Llama-3.3-70B",
                "analyzed_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze action plan efficacy: {str(e)}"
        ) 