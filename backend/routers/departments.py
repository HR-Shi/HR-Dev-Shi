from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas
from database import get_db
from auth.dependencies import get_current_active_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)

# Helper function for admin access
def require_admin_access(current_user: models.User = Depends(get_current_active_user)):
    if current_user.role not in ["admin", "hr_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.get("/", response_model=List[schemas.Department])
async def get_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all departments"""
    try:
        departments = db.query(models.Department).offset(skip).limit(limit).all()
        return departments
        
    except Exception as e:
        logger.error(f"Failed to get departments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve departments"
        )

@router.get("/{department_id}", response_model=schemas.Department)
async def get_department(
    department_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific department"""
    try:
        department = db.query(models.Department).filter(
            models.Department.id == department_id
        ).first()
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        return department
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get department {department_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve department"
        )

@router.post("/", response_model=schemas.Department)
async def create_department(
    department: schemas.DepartmentCreate,
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Create a new department (Admin only)"""
    try:
        # Check if department already exists
        existing = db.query(models.Department).filter(
            models.Department.name == department.name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department already exists"
            )
        
        db_department = models.Department(**department.dict())
        db.add(db_department)
        db.commit()
        db.refresh(db_department)
        
        logger.info(f"Department created by {current_user.email}: {department.name}")
        return db_department
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create department: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create department"
        )

@router.put("/{department_id}", response_model=schemas.Department)
async def update_department(
    department_id: str,
    department_update: schemas.DepartmentUpdate,
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Update a department (Admin only)"""
    try:
        department = db.query(models.Department).filter(
            models.Department.id == department_id
        ).first()
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        # Check if new name conflicts with existing department
        if department_update.name and department_update.name != department.name:
            existing = db.query(models.Department).filter(
                models.Department.name == department_update.name,
                models.Department.id != department_id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department name already exists"
                )
        
        # Update fields
        for field, value in department_update.dict(exclude_unset=True).items():
            setattr(department, field, value)
        
        db.commit()
        db.refresh(department)
        
        logger.info(f"Department updated by {current_user.email}: {department.name}")
        return department
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update department {department_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update department"
        )

@router.delete("/{department_id}")
async def delete_department(
    department_id: str,
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Delete a department (Admin only)"""
    try:
        department = db.query(models.Department).filter(
            models.Department.id == department_id
        ).first()
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        # Check if department has employees
        employee_count = db.query(models.Employee).filter(
            models.Employee.department_id == department_id
        ).count()
        
        if employee_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete department with {employee_count} employees. Please reassign employees first."
            )
        
        db.delete(department)
        db.commit()
        
        logger.info(f"Department deleted by {current_user.email}: {department.name}")
        return {"message": "Department deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete department {department_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete department"
        )

@router.get("/{department_id}/employees", response_model=List[schemas.Employee])
async def get_department_employees(
    department_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all employees in a department"""
    try:
        # Check if department exists
        department = db.query(models.Department).filter(
            models.Department.id == department_id
        ).first()
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        employees = db.query(models.Employee).filter(
            models.Employee.department_id == department_id
        ).offset(skip).limit(limit).all()
        
        return employees
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get employees for department {department_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve department employees"
        )

@router.get("/{department_id}/stats")
async def get_department_stats(
    department_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get department statistics"""
    try:
        # Check if department exists
        department = db.query(models.Department).filter(
            models.Department.id == department_id
        ).first()
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        # Get statistics
        total_employees = db.query(models.Employee).filter(
            models.Employee.department_id == department_id
        ).count()
        
        active_employees = db.query(models.Employee).filter(
            models.Employee.department_id == department_id,
            models.Employee.is_active == True
        ).count()
        
        # Get surveys targeting this department
        department_surveys = db.query(models.Survey).filter(
            models.Survey.target_departments.contains([str(department_id)])
        ).count()
        
        stats = {
            "department_name": department.name,
            "total_employees": total_employees,
            "active_employees": active_employees,
            "inactive_employees": total_employees - active_employees,
            "targeted_surveys": department_surveys,
        }
        
        return {
            "success": True,
            "message": "Department statistics retrieved successfully",
            "data": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get stats for department {department_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve department statistics"
        )

@router.get("/stats/summary")
async def get_all_departments_stats(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get overall department statistics"""
    try:
        total_departments = db.query(models.Department).count()
        
        # Get department employee counts
        dept_stats = db.execute("""
            SELECT 
                d.id,
                d.name,
                COUNT(e.id) as employee_count,
                COUNT(CASE WHEN e.is_active = true THEN 1 END) as active_count
            FROM departments d
            LEFT JOIN employees e ON d.id = e.department_id
            GROUP BY d.id, d.name
            ORDER BY employee_count DESC
        """).fetchall()
        
        departments_with_stats = []
        total_employees = 0
        
        for dept in dept_stats:
            dept_data = {
                "id": dept.id,
                "name": dept.name,
                "employee_count": dept.employee_count,
                "active_employees": dept.active_count
            }
            departments_with_stats.append(dept_data)
            total_employees += dept.employee_count
        
        summary = {
            "total_departments": total_departments,
            "total_employees": total_employees,
            "departments": departments_with_stats,
            "average_size": round(total_employees / total_departments, 2) if total_departments > 0 else 0
        }
        
        return {
            "success": True,
            "message": "Department summary retrieved successfully",
            "data": summary
        }
        
    except Exception as e:
        logger.error(f"Failed to get department summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve department summary"
        ) 