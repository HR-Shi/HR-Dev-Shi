from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid

from database import get_db
from models import (
    FocusGroup, Outlier, Employee, Department, User, 
    Survey, SurveyResponse, KPI, KPIValue
)
from schemas import (
    FocusGroupCreate, FocusGroupUpdate, FocusGroupResponse, FocusGroupList,
    FocusGroupMemberCreate, FocusGroupMemberResponse,
    FocusGroupAnalytics, OutlierDetectionResult, EmployeeOutlierInfo
)
from auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/focus-groups", tags=["focus-groups"])

@router.get("", response_model=FocusGroupList)
async def list_focus_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    group_type: Optional[str] = None,
    department_id: Optional[uuid.UUID] = None,
    is_active: Optional[bool] = None,
    created_by: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List focus groups with filtering and pagination"""
    query = select(FocusGroup)
    count_query = select(func.count(FocusGroup.id))
    
    # Apply filters
    filters = []
    if group_type:
        filters.append(FocusGroup.group_type == group_type)
    if department_id:
        filters.append(FocusGroup.department_id == department_id)
    if is_active is not None:
        filters.append(FocusGroup.is_active == is_active)
    if created_by:
        filters.append(FocusGroup.created_by == created_by)
    
    # Apply role-based filtering
    if current_user.role not in ["admin", "hr_admin"]:
        if current_user.role == "manager":
            # Managers can see groups for their department
            filters.append(FocusGroup.department_id == current_user.department_id)
        else:
            # Employees can see groups they're part of
            # We'll filter this after getting the results since we're using JSON arrays
            pass
    
    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(FocusGroup.created_at.desc())
    result = await db.execute(query)
    focus_groups = result.scalars().all()
    
    # Filter for employees - only show groups they're part of
    if current_user.role not in ["admin", "hr_admin", "manager"]:
        focus_groups = [
            fg for fg in focus_groups 
            if fg.members and str(current_user.id) in [str(m) for m in fg.members]
        ]
        total = len(focus_groups)
    
    return FocusGroupList(
        items=focus_groups,
        total=total,
        skip=skip,
        limit=limit
    )

@router.post("", response_model=FocusGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_focus_group(
    focus_group: FocusGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hr_admin", "manager"]))
):
    """Create a new focus group"""
    # Validate department exists if provided
    if focus_group.department_id:
        dept_result = await db.execute(
            select(Department).where(Department.id == focus_group.department_id)
        )
        if not dept_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid department_id"
            )
    
    # If manager, can only create groups for their department
    if current_user.role == "manager":
        if not focus_group.department_id or focus_group.department_id != current_user.department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers can only create focus groups for their department"
            )
    
    db_focus_group = FocusGroup(
        **focus_group.dict(),
        created_by=current_user.id
    )
    
    db.add(db_focus_group)
    await db.commit()
    await db.refresh(db_focus_group)
    
    return db_focus_group

@router.get("/{focus_group_id}", response_model=FocusGroupResponse)
async def get_focus_group(
    focus_group_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific focus group"""
    result = await db.execute(
        select(FocusGroup).where(FocusGroup.id == focus_group_id)
    )
    focus_group = result.scalar_one_or_none()
    
    if not focus_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Focus group not found"
        )
    
    # Check permissions
    if current_user.role not in ["admin", "hr_admin"]:
        if current_user.role == "manager":
            if focus_group.department_id != current_user.department_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        else:
            # Check if employee is a member of this group
            members = focus_group.members or []
            if str(current_user.id) not in [str(m) for m in members]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
    
    return focus_group

@router.put("/{focus_group_id}", response_model=FocusGroupResponse)
async def update_focus_group(
    focus_group_id: uuid.UUID,
    focus_group_update: FocusGroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a focus group"""
    result = await db.execute(
        select(FocusGroup).where(FocusGroup.id == focus_group_id)
    )
    focus_group = result.scalar_one_or_none()
    
    if not focus_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Focus group not found"
        )
    
    # Check permissions
    can_edit = (
        current_user.role in ["admin", "hr_admin"] or
        focus_group.created_by == current_user.id or
        (current_user.role == "manager" and focus_group.department_id == current_user.department_id)
    )
    
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    update_data = focus_group_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(focus_group, field, value)
    
    focus_group.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(focus_group)
    
    return focus_group

@router.delete("/{focus_group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_focus_group(
    focus_group_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hr_admin"]))
):
    """Delete a focus group"""
    result = await db.execute(
        select(FocusGroup).where(FocusGroup.id == focus_group_id)
    )
    focus_group = result.scalar_one_or_none()
    
    if not focus_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Focus group not found"
        )
    
    # Delete all members first
    await db.execute(
        delete(FocusGroupMember).where(FocusGroupMember.focus_group_id == focus_group_id)
    )
    
    # Delete the focus group
    await db.execute(
        delete(FocusGroup).where(FocusGroup.id == focus_group_id)
    )
    
    await db.commit()

# Focus Group Members
@router.get("/{focus_group_id}/members", response_model=List[uuid.UUID])
async def list_focus_group_members(
    focus_group_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List members of a focus group"""
    # Verify focus group exists and user has access
    focus_group = await get_focus_group(focus_group_id, db, current_user)
    
    # Return members from JSON column
    return focus_group.members or []

@router.post("/{focus_group_id}/members", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def add_focus_group_member(
    focus_group_id: uuid.UUID,
    employee_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a member to a focus group"""
    # Verify focus group exists and user has access
    focus_group = await get_focus_group(focus_group_id, db, current_user)
    
    # Check if user can edit this focus group
    can_edit = (
        current_user.role in ["admin", "hr_admin"] or
        focus_group.created_by == current_user.id
    )
    
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Verify employee exists
    employee_result = await db.execute(
        select(Employee).where(Employee.id == employee_id)
    )
    employee = employee_result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid employee_id"
        )
    
    # Check if member already exists
    members = focus_group.members or []
    if str(employee_id) in [str(m) for m in members]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee is already a member of this focus group"
        )
    
    # Add member to JSON array
    members.append(str(employee_id))
    focus_group.members = members
    focus_group.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(focus_group)
    
    return {
        "employee_id": str(employee_id),
        "added_at": datetime.utcnow().isoformat(),
        "added_by": str(current_user.id)
    }

@router.delete("/{focus_group_id}/members/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_focus_group_member(
    focus_group_id: uuid.UUID,
    employee_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a member from a focus group"""
    # Verify focus group exists and user has access
    focus_group = await get_focus_group(focus_group_id, db, current_user)
    
    # Check if user can edit this focus group
    can_edit = (
        current_user.role in ["admin", "hr_admin"] or
        focus_group.created_by == current_user.id
    )
    
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Remove member from JSON array
    members = focus_group.members or []
    original_length = len(members)
    members = [m for m in members if str(m) != str(employee_id)]
    
    if len(members) == original_length:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this focus group"
        )
    
    focus_group.members = members
    focus_group.updated_at = datetime.utcnow()
    
    await db.commit()

# Outlier Detection
@router.post("/detect-outliers", response_model=OutlierDetectionResult)
async def detect_outliers(
    survey_id: Optional[uuid.UUID] = None,
    kpi_id: Optional[uuid.UUID] = None,
    department_id: Optional[uuid.UUID] = None,
    threshold: float = Query(2.0, ge=1.0, le=3.0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hr_admin", "manager"]))
):
    """
    Detect outlier employees based on survey responses or KPI values.
    Uses statistical analysis to identify employees with significantly different scores.
    """
    outliers = []
    
    if survey_id:
        # Detect outliers based on survey responses
        outliers = await _detect_survey_outliers(db, survey_id, department_id, threshold)
    elif kpi_id:
        # Detect outliers based on KPI values
        outliers = await _detect_kpi_outliers(db, kpi_id, department_id, threshold)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either survey_id or kpi_id must be provided"
        )
    
    return OutlierDetectionResult(
        outliers=outliers,
        total_outliers=len(outliers),
        threshold_used=threshold,
        detection_criteria="statistical_deviation",
        detected_at=datetime.utcnow()
    )

async def _detect_survey_outliers(
    db: AsyncSession, 
    survey_id: uuid.UUID, 
    department_id: Optional[uuid.UUID], 
    threshold: float
) -> List[EmployeeOutlierInfo]:
    """Detect outliers based on survey response scores"""
    # Get all responses for the survey
    query = select(SurveyResponse).where(SurveyResponse.survey_id == survey_id)
    
    if department_id:
        query = query.join(Employee).where(Employee.department_id == department_id)
    
    result = await db.execute(query)
    responses = result.scalars().all()
    
    if len(responses) < 3:  # Need at least 3 responses for statistical analysis
        return []
    
    # Calculate average scores per employee
    employee_scores = {}
    for response in responses:
        if response.employee_id not in employee_scores:
            employee_scores[response.employee_id] = []
        
        # Calculate average score from response data
        if response.response_data and isinstance(response.response_data, dict):
            scores = [v for v in response.response_data.values() if isinstance(v, (int, float))]
            if scores:
                avg_score = sum(scores) / len(scores)
                employee_scores[response.employee_id].append(avg_score)
    
    # Calculate final average score per employee
    final_scores = {}
    for emp_id, scores in employee_scores.items():
        if scores:
            final_scores[emp_id] = sum(scores) / len(scores)
    
    if len(final_scores) < 3:
        return []
    
    # Calculate mean and standard deviation
    all_scores = list(final_scores.values())
    mean_score = sum(all_scores) / len(all_scores)
    variance = sum((x - mean_score) ** 2 for x in all_scores) / len(all_scores)
    std_dev = variance ** 0.5
    
    # Identify outliers (scores beyond threshold standard deviations)
    outliers = []
    for emp_id, score in final_scores.items():
        z_score = abs(score - mean_score) / std_dev if std_dev > 0 else 0
        
        if z_score > threshold:
            # Get employee details
            emp_result = await db.execute(
                select(Employee).where(Employee.id == emp_id)
            )
            employee = emp_result.scalar_one_or_none()
            
            if employee:
                outliers.append(EmployeeOutlierInfo(
                    employee_id=emp_id,
                    employee_name=f"{employee.first_name} {employee.last_name}",
                    score=round(score, 2),
                    z_score=round(z_score, 2),
                    deviation_type="low" if score < mean_score else "high",
                    confidence_level=min(99, round((z_score / 3) * 100, 1))
                ))
    
    return outliers

async def _detect_kpi_outliers(
    db: AsyncSession, 
    kpi_id: uuid.UUID, 
    department_id: Optional[uuid.UUID], 
    threshold: float
) -> List[EmployeeOutlierInfo]:
    """Detect outliers based on KPI values"""
    # Get recent KPI values
    query = select(KPIValue).where(KPIValue.kpi_id == kpi_id)
    
    if department_id:
        query = query.where(KPIValue.department_id == department_id)
    
    # Get values from the last 30 days
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    query = query.where(KPIValue.recorded_at >= thirty_days_ago)
    
    result = await db.execute(query)
    kpi_values = result.scalars().all()
    
    if len(kpi_values) < 3:
        return []
    
    # Group by employee and get latest values
    employee_values = {}
    for kpi_value in kpi_values:
        if kpi_value.employee_id:
            if kpi_value.employee_id not in employee_values:
                employee_values[kpi_value.employee_id] = []
            employee_values[kpi_value.employee_id].append(kpi_value.value)
    
    # Calculate average values per employee
    final_values = {}
    for emp_id, values in employee_values.items():
        if values:
            final_values[emp_id] = sum(values) / len(values)
    
    if len(final_values) < 3:
        return []
    
    # Calculate mean and standard deviation
    all_values = list(final_values.values())
    mean_value = sum(all_values) / len(all_values)
    variance = sum((x - mean_value) ** 2 for x in all_values) / len(all_values)
    std_dev = variance ** 0.5
    
    # Identify outliers
    outliers = []
    for emp_id, value in final_values.items():
        z_score = abs(value - mean_value) / std_dev if std_dev > 0 else 0
        
        if z_score > threshold:
            # Get employee details
            emp_result = await db.execute(
                select(Employee).where(Employee.id == emp_id)
            )
            employee = emp_result.scalar_one_or_none()
            
            if employee:
                outliers.append(EmployeeOutlierInfo(
                    employee_id=emp_id,
                    employee_name=f"{employee.first_name} {employee.last_name}",
                    score=round(value, 2),
                    z_score=round(z_score, 2),
                    deviation_type="low" if value < mean_value else "high",
                    confidence_level=min(99, round((z_score / 3) * 100, 1))
                ))
    
    return outliers

@router.post("/create-from-outliers", response_model=FocusGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_focus_group_from_outliers(
    outliers: OutlierDetectionResult,
    group_name: str,
    group_description: str,
    department_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hr_admin", "manager"]))
):
    """Create a focus group automatically from detected outliers"""
    if not outliers.outliers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No outliers provided to create focus group"
        )
    
    # Create the focus group
    focus_group = FocusGroup(
        name=group_name,
        description=group_description,
        group_type="outlier_based",
        department_id=department_id,
        created_by=current_user.id,
        criteria=f"Auto-generated from outlier detection with threshold {outliers.threshold_used}"
    )
    
    db.add(focus_group)
    await db.commit()
    await db.refresh(focus_group)
    
    # Add outliers as members
    for outlier in outliers.outliers:
        member = FocusGroupMember(
            focus_group_id=focus_group.id,
            employee_id=outlier.employee_id,
            role="member",
            added_by=current_user.id,
            notes=f"Z-score: {outlier.z_score}, Deviation: {outlier.deviation_type}"
        )
        db.add(member)
    
    await db.commit()
    
    return focus_group

# Analytics
@router.get("/stats/summary", response_model=FocusGroupAnalytics)
async def get_focus_group_analytics(
    department_id: Optional[uuid.UUID] = None,
    group_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hr_admin", "manager"]))
):
    """Get focus group analytics and statistics"""
    query = select(FocusGroup)
    
    # Apply filters
    filters = []
    if department_id:
        filters.append(FocusGroup.department_id == department_id)
    if group_type:
        filters.append(FocusGroup.group_type == group_type)
        
    # Apply role-based filtering
    if current_user.role == "manager":
        filters.append(FocusGroup.department_id == current_user.department_id)
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    focus_groups = result.scalars().all()
    
    # Calculate statistics
    total_groups = len(focus_groups)
    active_groups = len([fg for fg in focus_groups if fg.is_active])
    inactive_groups = total_groups - active_groups
    
    # Group type distribution
    type_distribution = {}
    for fg in focus_groups:
        group_type = fg.group_type or "other"
        type_distribution[group_type] = type_distribution.get(group_type, 0) + 1
    
    # Get member count statistics
    member_counts = []
    for fg in focus_groups:
        member_result = await db.execute(
            select(func.count(FocusGroupMember.id)).where(
                FocusGroupMember.focus_group_id == fg.id
            )
        )
        member_count = member_result.scalar()
        member_counts.append(member_count)
    
    avg_members_per_group = sum(member_counts) / len(member_counts) if member_counts else 0
    total_members = sum(member_counts)
    
    return FocusGroupAnalytics(
        total_groups=total_groups,
        active_groups=active_groups,
        inactive_groups=inactive_groups,
        total_members=total_members,
        average_members_per_group=round(avg_members_per_group, 2),
        group_type_distribution=type_distribution
    ) 