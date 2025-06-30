from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas
from typing import List, Optional, Dict, Any
from datetime import datetime

# User CRUD operations
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Employee CRUD operations
def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_employee = models.Employee(
        user_id=employee.user_id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        position=employee.position,
        hire_date=employee.hire_date
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    # Add departments
    for dept_id in employee.department_ids:
        department = db.query(models.Department).filter(models.Department.id == dept_id).first()
        if department:
            db_employee.departments.append(department)
    
    db.commit()
    return db_employee

def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()

def get_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()

# Department CRUD operations
def create_department(db: Session, department: schemas.DepartmentCreate):
    db_department = models.Department(**department.dict())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

def get_department(db: Session, department_id: int):
    return db.query(models.Department).filter(models.Department.id == department_id).first()

def get_departments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Department).offset(skip).limit(limit).all()

# Survey CRUD operations
def create_survey(db: Session, survey: schemas.SurveyCreate):
    db_survey = models.Survey(**survey.dict())
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return db_survey

def get_survey(db: Session, survey_id: int):
    return db.query(models.Survey).filter(models.Survey.id == survey_id).first()

def get_surveys(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Survey).offset(skip).limit(limit).all()

def get_active_surveys(db: Session):
    return db.query(models.Survey).filter(models.Survey.is_active == True).all()

# Survey Response CRUD operations
def create_survey_response(db: Session, response: schemas.SurveyResponseCreate):
    db_response = models.SurveyResponse(**response.dict())
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response

def get_survey_responses(db: Session, survey_id: int):
    return db.query(models.SurveyResponse).filter(models.SurveyResponse.survey_id == survey_id).all()

# Performance Review CRUD operations
def create_performance_review(db: Session, review: schemas.PerformanceReviewCreate):
    db_review = models.PerformanceReview(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_performance_reviews(db: Session, employee_id: int):
    return db.query(models.PerformanceReview).filter(models.PerformanceReview.employee_id == employee_id).all()

# Action Plan CRUD operations
def create_action_plan(db: Session, action_plan: schemas.ActionPlanCreate):
    db_action_plan = models.ActionPlan(**action_plan.dict())
    db.add(db_action_plan)
    db.commit()
    db.refresh(db_action_plan)
    return db_action_plan

def get_action_plans(db: Session, department_id: int):
    return db.query(models.ActionPlan).filter(models.ActionPlan.target_department_id == department_id).all()

# KPI CRUD operations
def create_kpi(db: Session, kpi: schemas.KPICreate):
    db_kpi = models.KPI(**kpi.dict())
    db.add(db_kpi)
    db.commit()
    db.refresh(db_kpi)
    return db_kpi

def get_kpis(db: Session, department_id: int):
    return db.query(models.KPI).filter(models.KPI.department_id == department_id).all()

def update_kpi_value(db: Session, kpi_id: int, new_value: float):
    db_kpi = db.query(models.KPI).filter(models.KPI.id == kpi_id).first()
    if db_kpi:
        db_kpi.current_value = new_value
        db_kpi.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_kpi)
    return db_kpi 