from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
import models
import schemas
from database import get_db
from auth.dependencies import get_current_active_user, is_super_admin
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# User Permissions Matrix
USER_PERMISSIONS = {
    "admin": {
        "users": ["create", "read", "update", "delete"],
        "employees": ["create", "read", "update", "delete"],
        "departments": ["create", "read", "update", "delete"],
        "kpis": ["create", "read", "update", "delete"],
        "surveys": ["create", "read", "update", "delete"],
        "action_plans": ["create", "read", "update", "delete"],
        "focus_groups": ["create", "read", "update", "delete"],
        "analytics": ["read", "export"],
        "system": ["configure", "backup"]
    },
    "hr_admin": {
        "users": ["create", "read", "update"],
        "employees": ["create", "read", "update", "delete"],
        "departments": ["create", "read", "update"],
        "kpis": ["create", "read", "update"],
        "surveys": ["create", "read", "update", "delete"],
        "action_plans": ["create", "read", "update", "delete"],
        "focus_groups": ["create", "read", "update", "delete"],
        "analytics": ["read", "export"]
    },
    "manager": {
        "employees": ["read", "update"],  # Only in their department
        "kpis": ["read"],
        "surveys": ["read", "update"],  # Only their department surveys
        "action_plans": ["create", "read", "update"],  # Only their department
        "focus_groups": ["create", "read", "update"],  # Only their department
        "analytics": ["read"]  # Only their department data
    },
    "employee": {
        "surveys": ["read", "respond"],
        "action_plans": ["read"],  # Only assigned to them
        "focus_groups": ["read"],  # Only groups they're in
        "profile": ["read", "update"]  # Their own profile
    }
}

# Helper function to check admin permissions
def require_admin_access(current_user: models.User = Depends(get_current_active_user)):
    # Super admins can access everything
    if is_super_admin(current_user):
        return current_user
        
    if current_user.role not in ["admin", "hr_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

@router.get("/permissions/{role}")
async def get_role_permissions(
    role: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get permissions for a specific role"""
    try:
        if current_user.role not in ["admin", "hr_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to view role permissions"
            )
        
        if role not in USER_PERMISSIONS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        return {
            "role": role,
            "permissions": USER_PERMISSIONS[role]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get permissions for role {role}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve role permissions"
        )

@router.get("/permissions/matrix/all")
async def get_permissions_matrix(
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get complete permissions matrix for all roles"""
    try:
        return {
            "permissions_matrix": USER_PERMISSIONS,
            "roles": list(USER_PERMISSIONS.keys()),
            "resources": list(set().union(*[perms.keys() for perms in USER_PERMISSIONS.values()]))
        }
        
    except Exception as e:
        logger.error(f"Failed to get permissions matrix: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve permissions matrix"
        )

@router.get("/", response_model=List[schemas.User])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[schemas.UserRole] = None,
    is_active: Optional[bool] = None,
    department_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get all users with advanced filtering (Admin only)"""
    try:
        query = db.query(models.User).join(models.Employee, models.User.employee_id == models.Employee.id, isouter=True)
        
        if role:
            query = query.filter(models.User.role == role)
        if is_active is not None:
            query = query.filter(models.User.is_active == is_active)
        if department_id:
            query = query.filter(models.Employee.department_id == department_id)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    models.User.email.ilike(search_term),
                    models.Employee.first_name.ilike(search_term),
                    models.Employee.last_name.ilike(search_term),
                    models.Employee.position.ilike(search_term)
                )
            )
        
        users = query.offset(skip).limit(limit).all()
        return users
        
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.get("/{user_id}", response_model=schemas.User)
async def get_user_by_id(
    user_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (Admin or self only)"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions: admin/hr_admin can view any user, others can only view themselves
        if current_user.role not in ["admin", "hr_admin"] and current_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )

@router.get("/{user_id}/profile")
async def get_user_profile(
    user_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive user profile including employee data and department info"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions: admin/hr_admin can view any user, others can only view themselves
        if current_user.role not in ["admin", "hr_admin"] and current_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Get employee data if linked
        employee_data = None
        department_data = None
        manager_data = None
        
        if user.employee_id:
            employee = db.query(models.Employee).filter(models.Employee.id == user.employee_id).first()
            if employee:
                employee_data = {
                    "id": employee.id,
                    "first_name": employee.first_name,
                    "last_name": employee.last_name,
                    "position": employee.position,
                    "hire_date": employee.hire_date,
                    "status": employee.status,
                    "phone": employee.phone,
                    "skills": employee.skills,
                    "competencies": employee.competencies
                }
                
                # Get department data
                if employee.department_id:
                    department = db.query(models.Department).filter(models.Department.id == employee.department_id).first()
                    if department:
                        department_data = {
                            "id": department.id,
                            "name": department.name,
                            "description": department.description
                        }
                
                # Get manager data
                if employee.manager_id:
                    manager = db.query(models.Employee).filter(models.Employee.id == employee.manager_id).first()
                    if manager:
                        manager_data = {
                            "id": manager.id,
                            "name": f"{manager.first_name} {manager.last_name}",
                            "position": manager.position,
                            "email": manager.email
                        }
        
        # Get user permissions
        user_permissions = USER_PERMISSIONS.get(user.role, {})
        
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "last_login": user.last_login,
                "profile_settings": user.profile_settings,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            },
            "employee": employee_data,
            "department": department_data,
            "manager": manager_data,
            "permissions": user_permissions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user profile {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )

@router.put("/{user_id}/profile")
async def update_user_profile(
    user_id: str,
    profile_update: Dict[str, Any],
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile settings"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions
        if current_user.role not in ["admin", "hr_admin"] and current_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Update profile settings
        current_settings = user.profile_settings or {}
        current_settings.update(profile_update)
        user.profile_settings = current_settings
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User profile updated by {current_user.email}: {user.email}")
        return {"message": "Profile updated successfully", "profile_settings": user.profile_settings}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user profile {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )

@router.post("/", response_model=schemas.User)
async def create_user(
    user: schemas.UserCreate,
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Create a new user (Admin only)"""
    try:
        # Check if user already exists
        existing_user = db.query(models.User).filter(
            models.User.email == user.email
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = auth.get_password_hash(user.password)
        db_user = models.User(
            email=user.email,
            hashed_password=hashed_password,
            role=user.role,
            is_active=user.is_active,
            employee_id=user.employee_id
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User created by {current_user.email}: {user.email}")
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: str,
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user (Admin or self only)"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions
        if current_user.role not in ["admin", "hr_admin"] and current_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Non-admin users can't change their own role
        if current_user.role not in ["admin", "hr_admin"] and "role" in user_update.dict(exclude_unset=True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change your own role"
            )
        
        # Update user fields
        for field, value in user_update.dict(exclude_unset=True).items():
            if field == "email" and value != user.email:
                # Check if new email is already taken
                existing_user = db.query(models.User).filter(
                    models.User.email == value,
                    models.User.id != user.id
                ).first()
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already in use"
                    )
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User updated by {current_user.email}: {user.email}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Delete user (Admin only)"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Don't allow deleting yourself
        if current_user.id == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        db.delete(user)
        db.commit()
        
        logger.info(f"User deleted by {current_user.email}: {user.email}")
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Deactivate user (Admin only)"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Don't allow deactivating yourself
        if current_user.id == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )
        
        user.is_active = False
        db.commit()
        
        logger.info(f"User deactivated by {current_user.email}: {user.email}")
        return {"message": "User deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deactivate user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user"
        )

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Activate user (Admin only)"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = True
        db.commit()
        
        logger.info(f"User activated by {current_user.email}: {user.email}")
        return {"message": "User activated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to activate user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate user"
        )

@router.post("/bulk/assign-department")
async def bulk_assign_department(
    user_ids: List[str],
    department_id: uuid.UUID,
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Bulk assign users to a department"""
    try:
        # Verify department exists
        department = db.query(models.Department).filter(models.Department.id == department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        updated_count = 0
        failed_users = []
        
        for user_id in user_ids:
            try:
                user = db.query(models.User).filter(models.User.id == user_id).first()
                if not user or not user.employee_id:
                    failed_users.append(user_id)
                    continue
                
                employee = db.query(models.Employee).filter(models.Employee.id == user.employee_id).first()
                if employee:
                    employee.department_id = department_id
                    employee.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    failed_users.append(user_id)
                    
            except Exception as e:
                logger.error(f"Failed to assign user {user_id} to department: {e}")
                failed_users.append(user_id)
        
        db.commit()
        
        logger.info(f"Bulk department assignment by {current_user.email}: {updated_count} users assigned to {department.name}")
        
        return {
            "message": f"Successfully assigned {updated_count} users to department",
            "department": department.name,
            "updated_count": updated_count,
            "failed_users": failed_users
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed bulk department assignment: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign users to department"
        )

@router.post("/bulk/update-roles")
async def bulk_update_roles(
    role_updates: List[Dict[str, str]],  # [{"user_id": "...", "role": "..."}]
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Bulk update user roles"""
    try:
        updated_count = 0
        failed_updates = []
        
        for update in role_updates:
            try:
                user_id = update.get("user_id")
                new_role = update.get("role")
                
                if not user_id or not new_role:
                    failed_updates.append({"user_id": user_id, "error": "Missing user_id or role"})
                    continue
                
                if new_role not in USER_PERMISSIONS:
                    failed_updates.append({"user_id": user_id, "error": "Invalid role"})
                    continue
                
                user = db.query(models.User).filter(models.User.id == user_id).first()
                if not user:
                    failed_updates.append({"user_id": user_id, "error": "User not found"})
                    continue
                
                user.role = new_role
                user.updated_at = datetime.utcnow()
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to update role for user {user_id}: {e}")
                failed_updates.append({"user_id": user_id, "error": str(e)})
        
        db.commit()
        
        logger.info(f"Bulk role update by {current_user.email}: {updated_count} users updated")
        
        return {
            "message": f"Successfully updated {updated_count} user roles",
            "updated_count": updated_count,
            "failed_updates": failed_updates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed bulk role update: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user roles"
        )

@router.get("/analytics/department-distribution")
async def get_user_department_distribution(
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get user distribution across departments"""
    try:
        # Get user count by department
        query = db.query(
            models.Department.name.label('department_name'),
            func.count(models.User.id).label('user_count')
        ).join(
            models.Employee, models.Department.id == models.Employee.department_id
        ).join(
            models.User, models.Employee.id == models.User.employee_id
        ).filter(
            models.User.is_active == True
        ).group_by(models.Department.id, models.Department.name)
        
        department_distribution = query.all()
        
        # Get users without department
        users_without_dept = db.query(func.count(models.User.id)).filter(
            and_(
                models.User.is_active == True,
                or_(
                    models.User.employee_id.is_(None),
                    models.User.employee_id.in_(
                        db.query(models.Employee.id).filter(models.Employee.department_id.is_(None))
                    )
                )
            )
        ).scalar()
        
        result = [
            {"department": dept.department_name, "user_count": dept.user_count}
            for dept in department_distribution
        ]
        
        if users_without_dept > 0:
            result.append({"department": "Unassigned", "user_count": users_without_dept})
        
        return {
            "department_distribution": result,
            "total_active_users": sum(item["user_count"] for item in result)
        }
        
    except Exception as e:
        logger.error(f"Failed to get department distribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve department distribution"
        )

@router.get("/analytics/role-distribution")
async def get_user_role_distribution(
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get user distribution by role"""
    try:
        query = db.query(
            models.User.role,
            func.count(models.User.id).label('user_count')
        ).filter(
            models.User.is_active == True
        ).group_by(models.User.role)
        
        role_distribution = query.all()
        
        return {
            "role_distribution": [
                {"role": role_data.role, "user_count": role_data.user_count}
                for role_data in role_distribution
            ],
            "total_active_users": sum(role_data.user_count for role_data in role_distribution)
        }
        
    except Exception as e:
        logger.error(f"Failed to get role distribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve role distribution"
        )

@router.get("/me/permissions")
async def get_my_permissions(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's permissions and capabilities"""
    try:
        permissions = USER_PERMISSIONS.get(current_user.role, {})
        
        # Super admins get all permissions
        if auth.is_super_admin(current_user):
            permissions = USER_PERMISSIONS.get("admin", {})
            permissions["system"] = ["configure", "backup", "super_admin"]
        
        return {
            "user_id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
            "is_super_admin": auth.is_super_admin(current_user),
            "permissions": permissions,
            "profile_settings": current_user.profile_settings
        }
        
    except Exception as e:
        logger.error(f"Failed to get user permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user permissions"
        )

@router.get("/stats/summary")
async def get_user_stats(
    current_user: models.User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get user statistics (Admin only)"""
    try:
        stats = {
            "total_users": db.query(models.User).count(),
            "active_users": db.query(models.User).filter(models.User.is_active == True).count(),
            "inactive_users": db.query(models.User).filter(models.User.is_active == False).count(),
            "admins": db.query(models.User).filter(models.User.role == "admin").count(),
            "hr_admins": db.query(models.User).filter(models.User.role == "hr_admin").count(),
            "managers": db.query(models.User).filter(models.User.role == "manager").count(),
            "employees": db.query(models.User).filter(models.User.role == "employee").count(),
            "users_without_passwords": db.query(models.User).filter(models.User.hashed_password.is_(None)).count(),
            "super_admins": len([u for u in db.query(models.User).all() if auth.is_super_admin(u)]),
        }
        
        return {
            "success": True,
            "message": "User statistics retrieved successfully",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        ) 