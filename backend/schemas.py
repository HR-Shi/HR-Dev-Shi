from pydantic import BaseModel, validator, EmailStr, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
import uuid
from decimal import Decimal

# =====================================================
# ENUMS FOR TYPE SAFETY
# =====================================================

class UserRole(str, Enum):
    ADMIN = "admin"
    HR_ADMIN = "hr_admin" 
    MANAGER = "manager"
    EMPLOYEE = "employee"

class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"

class SurveyType(str, Enum):
    BASELINE = "baseline"
    PULSE = "pulse"
    CUSTOM = "custom"
    PERFORMANCE = "performance"
    EXIT = "exit"

class SurveyStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ActionPlanStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class OutlierSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MeasurementType(str, Enum):
    BASELINE = "baseline"
    INTERIM = "interim"
    FINAL = "final"

# =====================================================
# BASE SCHEMAS
# =====================================================

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        use_enum_values = True

# =====================================================
# USER & AUTHENTICATION SCHEMAS
# =====================================================

class UserBase(BaseSchema):
    email: EmailStr
    role: UserRole = UserRole.EMPLOYEE
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    employee_id: Optional[uuid.UUID] = None

class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    profile_settings: Optional[Dict[str, Any]] = None

class User(UserBase):
    id: uuid.UUID
    employee_id: Optional[uuid.UUID] = None
    last_login: Optional[datetime] = None
    profile_settings: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

class UserLogin(BaseSchema):
    email: EmailStr
    password: str

class Token(BaseSchema):
    access_token: str
    token_type: str
    user: User

# =====================================================
# DEPARTMENT SCHEMAS
# =====================================================

class DepartmentBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    manager_id: Optional[uuid.UUID] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    manager_id: Optional[uuid.UUID] = None

class Department(DepartmentBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

# =====================================================
# EMPLOYEE SCHEMAS
# =====================================================

class EmployeeBase(BaseSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: Optional[str] = None
    department_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    position: str = Field(..., min_length=1, max_length=100)
    hire_date: date
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    is_active: bool = True

class EmployeeCreate(EmployeeBase):
    profile_data: Optional[Dict[str, Any]] = {}
    skills: Optional[List[str]] = []
    competencies: Optional[Dict[str, Any]] = {}

class EmployeeUpdate(BaseSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    position: Optional[str] = Field(None, min_length=1, max_length=100)
    hire_date: Optional[date] = None
    status: Optional[EmployeeStatus] = None
    is_active: Optional[bool] = None
    profile_data: Optional[Dict[str, Any]] = None
    skills: Optional[List[str]] = None
    competencies: Optional[Dict[str, Any]] = None

class Employee(EmployeeBase):
    id: uuid.UUID
    profile_data: Dict[str, Any] = {}
    skills: List[str] = []
    competencies: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

# =====================================================
# KPI SCHEMAS
# =====================================================

class KPICategoryBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class KPICategoryCreate(KPICategoryBase):
    pass

class KPICategory(KPICategoryBase):
    id: uuid.UUID
    created_at: datetime

class KPIBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    target_value: Optional[Decimal] = None
    current_value: Optional[Decimal] = Field(default=0)
    unit: Optional[str] = None
    measurement_frequency: str = Field(..., pattern="^(daily|weekly|monthly|quarterly|yearly)$")
    calculation_method: Optional[str] = Field(None, pattern="^(manual|automatic|survey_based)$")
    is_custom: bool = False
    is_active: bool = True
    target_departments: List[uuid.UUID] = []
    target_employee_groups: List[uuid.UUID] = []
    alert_threshold_low: Optional[Decimal] = None
    alert_threshold_high: Optional[Decimal] = None

class KPICreate(KPIBase):
    created_by: uuid.UUID

class KPIUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    target_value: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    unit: Optional[str] = None
    measurement_frequency: Optional[str] = Field(None, pattern="^(daily|weekly|monthly|quarterly|yearly)$")
    calculation_method: Optional[str] = Field(None, pattern="^(manual|automatic|survey_based)$")
    is_active: Optional[bool] = None
    target_departments: Optional[List[uuid.UUID]] = None
    target_employee_groups: Optional[List[uuid.UUID]] = None
    alert_threshold_low: Optional[Decimal] = None
    alert_threshold_high: Optional[Decimal] = None

class KPI(KPIBase):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

class KPIValueBase(BaseSchema):
    kpi_id: uuid.UUID
    value: Decimal
    period_start: datetime
    period_end: datetime
    department_id: Optional[uuid.UUID] = None
    metadata: Dict[str, Any] = {}

class KPIValueCreate(KPIValueBase):
    pass

class KPIValue(KPIValueBase):
    id: uuid.UUID
    created_at: datetime

# =====================================================
# SURVEY SCHEMAS
# =====================================================

class SurveyQuestionBase(BaseSchema):
    text: str = Field(..., min_length=1)
    type: str = Field(..., pattern="^(text|scale|boolean|multiple_choice|single_choice)$")
    options: Optional[List[str]] = None
    required: bool = True
    order: int = Field(default=1, ge=1)

class SurveyQuestionCreate(SurveyQuestionBase):
    pass

class SurveyQuestion(SurveyQuestionBase):
    id: uuid.UUID
    survey_id: uuid.UUID
    created_at: datetime

class SurveyTemplateBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[SurveyType] = None
    questions: List[SurveyQuestionCreate]
    is_predefined: bool = False
    tags: List[str] = []

class SurveyTemplateCreate(SurveyTemplateBase):
    created_by: uuid.UUID

class SurveyTemplate(SurveyTemplateBase):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

class SurveyBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: SurveyType
    status: SurveyStatus = SurveyStatus.DRAFT
    start_date: Optional[datetime] = None
    end_date: datetime
    is_anonymous: bool = False
    target_departments: List[uuid.UUID] = []
    target_employees: List[uuid.UUID] = []
    frequency: str = Field(default="one-time", pattern="^(one-time|daily|weekly|monthly|quarterly)$")
    platform_integrations: Dict[str, Any] = {}

class SurveyCreate(SurveyBase):
    questions: List[SurveyQuestionCreate] = []

class SurveyUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    type: Optional[SurveyType] = None
    status: Optional[SurveyStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_anonymous: Optional[bool] = None
    target_departments: Optional[List[uuid.UUID]] = None
    target_employees: Optional[List[uuid.UUID]] = None
    frequency: Optional[str] = Field(None, pattern="^(one-time|daily|weekly|monthly|quarterly)$")
    platform_integrations: Optional[Dict[str, Any]] = None

class Survey(SurveyBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class SurveyResponseBase(BaseSchema):
    survey_id: uuid.UUID
    employee_id: uuid.UUID
    responses: Dict[str, Any]
    completion_time_seconds: Optional[int] = None
    is_anonymous: bool = False
    metadata: Dict[str, Any] = {}

class SurveyResponseCreate(SurveyResponseBase):
    pass

class SurveyResponse(SurveyResponseBase):
    id: uuid.UUID
    submitted_at: datetime

# =====================================================
# FOCUS GROUP SCHEMAS
# =====================================================

class FocusGroupBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: str = Field(..., pattern="^(department|role|performance|survey_based|custom)$")
    criteria: Dict[str, Any]
    members: List[uuid.UUID]
    status: str = Field(default="active", pattern="^(active|archived|dissolved)$")

class FocusGroupCreate(FocusGroupBase):
    created_by: uuid.UUID

class FocusGroupUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    type: Optional[str] = Field(None, pattern="^(department|role|performance|survey_based|custom)$")
    criteria: Optional[Dict[str, Any]] = None
    members: Optional[List[uuid.UUID]] = None
    status: Optional[str] = Field(None, pattern="^(active|archived|dissolved)$")

class FocusGroup(FocusGroupBase):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

# =====================================================
# OUTLIER SCHEMAS
# =====================================================

class OutlierBase(BaseSchema):
    employee_id: uuid.UUID
    type: str = Field(..., pattern="^(kpi_based|survey_based|performance_based)$")
    category: str = Field(..., pattern="^(engagement|stress|performance|attendance)$")
    severity: OutlierSeverity
    metrics: Dict[str, Any]
    contributing_factors: List[str] = []
    is_resolved: bool = False
    focus_group_id: Optional[uuid.UUID] = None

class OutlierCreate(OutlierBase):
    pass

class OutlierUpdate(BaseSchema):
    is_resolved: Optional[bool] = None
    focus_group_id: Optional[uuid.UUID] = None
    resolved_at: Optional[datetime] = None

class Outlier(OutlierBase):
    id: uuid.UUID
    identified_at: datetime
    resolved_at: Optional[datetime] = None

# =====================================================
# ACTION PLAN SCHEMAS
# =====================================================

class ActionPlanTemplateBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = Field(..., min_length=1)
    steps: List[Dict[str, Any]]
    estimated_duration_days: Optional[int] = Field(None, ge=1)
    success_metrics: List[str] = []
    is_ai_generated: bool = False
    effectiveness_score: Optional[Decimal] = Field(None, ge=0, le=100)
    tags: List[str] = []

class ActionPlanTemplateCreate(ActionPlanTemplateBase):
    created_by: uuid.UUID

class ActionPlanTemplate(ActionPlanTemplateBase):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

class ActionPlanBase(BaseSchema):
    template_id: Optional[uuid.UUID] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    target_focus_group_id: Optional[uuid.UUID] = None
    target_departments: List[uuid.UUID] = []
    target_employees: List[uuid.UUID] = []
    target_kpis: List[uuid.UUID] = []
    status: ActionPlanStatus = ActionPlanStatus.PLANNED
    priority: Priority = Priority.MEDIUM
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    assigned_to: Optional[uuid.UUID] = None
    stakeholders: List[uuid.UUID] = []
    milestones: List[Dict[str, Any]] = []
    progress_percentage: int = Field(default=0, ge=0, le=100)
    budget: Optional[Decimal] = Field(None, ge=0)
    resources_required: List[str] = []

class ActionPlanCreate(ActionPlanBase):
    created_by: uuid.UUID

class ActionPlanUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    target_focus_group_id: Optional[uuid.UUID] = None
    target_departments: Optional[List[uuid.UUID]] = None
    target_employees: Optional[List[uuid.UUID]] = None
    target_kpis: Optional[List[uuid.UUID]] = None
    status: Optional[ActionPlanStatus] = None
    priority: Optional[Priority] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    assigned_to: Optional[uuid.UUID] = None
    stakeholders: Optional[List[uuid.UUID]] = None
    milestones: Optional[List[Dict[str, Any]]] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    budget: Optional[Decimal] = Field(None, ge=0)
    resources_required: Optional[List[str]] = None

class ActionPlan(ActionPlanBase):
    id: uuid.UUID
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

# =====================================================
# EFFICACY MEASUREMENT SCHEMAS
# =====================================================

class EfficacyMeasurementBase(BaseSchema):
    action_plan_id: uuid.UUID
    measurement_type: MeasurementType
    kpi_id: Optional[uuid.UUID] = None
    baseline_value: Optional[Decimal] = None
    measured_value: Optional[Decimal] = None
    improvement_percentage: Optional[Decimal] = None
    improvement_absolute: Optional[Decimal] = None
    statistical_significance: Optional[Decimal] = None
    measurement_date: datetime
    survey_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class EfficacyMeasurementCreate(EfficacyMeasurementBase):
    pass

class EfficacyMeasurement(EfficacyMeasurementBase):
    id: uuid.UUID
    created_at: datetime

# =====================================================
# PERFORMANCE MANAGEMENT SCHEMAS
# =====================================================

class PerformanceReviewCycleBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: str = Field(..., pattern="^(annual|quarterly|monthly|project_based)$")
    start_date: date
    end_date: date
    status: str = Field(default="planning", pattern="^(planning|active|review|completed)$")
    departments: List[uuid.UUID] = []
    template_config: Dict[str, Any] = {}

class PerformanceReviewCycleCreate(PerformanceReviewCycleBase):
    created_by: uuid.UUID

class PerformanceReviewCycle(PerformanceReviewCycleBase):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

class PerformanceReviewBase(BaseSchema):
    employee_id: uuid.UUID
    reviewer_id: uuid.UUID
    cycle_id: Optional[uuid.UUID] = None
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None
    status: str = Field(default="pending", pattern="^(pending|draft|submitted|approved|completed)$")
    self_assessment: Dict[str, Any] = {}
    peer_feedback: List[Dict[str, Any]] = []
    manager_feedback: Dict[str, Any] = {}
    goals_for_next_period: List[Dict[str, Any]] = []
    calibration_score: Optional[Decimal] = None
    review_type: str = Field(default="annual", pattern="^(annual|quarterly|monthly|project_based)$")

class PerformanceReviewCreate(PerformanceReviewBase):
    pass

class PerformanceReview(PerformanceReviewBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class FeedbackBase(BaseSchema):
    recipient_id: uuid.UUID
    giver_id: uuid.UUID
    feedback_type: str = Field(..., pattern="^(peer|upward|downward|self)$")
    category: Optional[str] = Field(None, pattern="^(performance|behavior|skills|communication)$")
    content: str = Field(..., min_length=1)
    rating: Optional[int] = Field(None, ge=1, le=5)
    is_anonymous: bool = False
    related_review_id: Optional[uuid.UUID] = None
    tags: List[str] = []

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: uuid.UUID
    created_at: datetime

# =====================================================
# ANALYTICS & DASHBOARD SCHEMAS
# =====================================================

class DashboardWidget(BaseSchema):
    type: str
    title: str
    config: Dict[str, Any]
    position: Dict[str, int]  # x, y, width, height

class DashboardConfigBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    layout: Dict[str, Any]
    widgets: List[DashboardWidget]
    is_default: bool = False
    is_shared: bool = False
    shared_with: List[uuid.UUID] = []

class DashboardConfigCreate(DashboardConfigBase):
    user_id: uuid.UUID

class DashboardConfig(DashboardConfigBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

# =====================================================
# ANALYTICS RESPONSE SCHEMAS
# =====================================================

class KPIDashboard(BaseSchema):
    id: uuid.UUID
    name: str
    description: Optional[str]
    current_value: Optional[Decimal]
    target_value: Optional[Decimal]
    unit: Optional[str]
    category_name: str
    category_color: Optional[str]
    achievement_percentage: Optional[Decimal]
    measurement_frequency: str
    is_active: bool

class EmployeeSummary(BaseSchema):
    id: uuid.UUID
    first_name: Optional[str]
    last_name: Optional[str]
    email: str
    position: str
    department_name: Optional[str]
    hire_date: date
    status: str
    is_active: bool
    manager_name: Optional[str]
    user_role: Optional[str]

class ActionPlanStatus(BaseSchema):
    id: uuid.UUID
    title: str
    status: str
    priority: str
    progress_percentage: int
    start_date: Optional[date]
    end_date: Optional[date]
    focus_group_name: Optional[str]
    assigned_to_email: Optional[str]
    created_by_email: Optional[str]
    total_milestones: int
    completed_milestones: int

# =====================================================
# API RESPONSE SCHEMAS
# =====================================================

class PaginationMeta(BaseSchema):
    page: int
    size: int
    total: int
    pages: int

class PaginatedResponse(BaseSchema):
    items: List[Any]
    meta: PaginationMeta

class APIResponse(BaseSchema):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None

# =====================================================
# VALIDATORS
# =====================================================

@validator('email')
def validate_email(cls, v):
    if not v or '@' not in v:
        raise ValueError('Invalid email address')
    return v.lower()

@validator('end_date')
def validate_end_date(cls, v, values):
    if 'start_date' in values and values['start_date'] and v <= values['start_date']:
        raise ValueError('End date must be after start date')
    return v 

# =====================================================
# ANALYTICS SCHEMAS FOR NEW ROUTERS
# =====================================================

# Action Plan Analytics
class ActionPlanAnalytics(BaseSchema):
    total_plans: int
    completed_plans: int
    in_progress_plans: int
    draft_plans: int
    overdue_plans: int
    average_progress: float
    completion_rate: float
    status_distribution: Dict[str, int]

class ActionPlanProgressUpdate(BaseSchema):
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[ActionPlanStatus] = None
    notes: Optional[str] = None

class ActionPlanList(BaseSchema):
    items: List[ActionPlan]
    total: int
    skip: int
    limit: int

class ActionPlanResponse(ActionPlan):
    pass

class ActionPlanTemplateResponse(ActionPlanTemplate):
    pass

class ActionPlanTemplateUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1)
    steps: Optional[List[Dict[str, Any]]] = None
    estimated_duration_days: Optional[int] = Field(None, ge=1)
    success_metrics: Optional[List[str]] = None
    is_ai_generated: Optional[bool] = None
    effectiveness_score: Optional[Decimal] = Field(None, ge=0, le=100)
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None

# Action Plan Milestones
class ActionPlanMilestoneBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: date
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed|overdue)$")
    completion_percentage: int = Field(default=0, ge=0, le=100)
    assigned_to: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class ActionPlanMilestoneCreate(ActionPlanMilestoneBase):
    pass

class ActionPlanMilestoneUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|overdue)$")
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    assigned_to: Optional[uuid.UUID] = None
    notes: Optional[str] = None

class ActionPlanMilestoneResponse(ActionPlanMilestoneBase):
    id: uuid.UUID
    action_plan_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

# Focus Group Analytics
class FocusGroupAnalytics(BaseSchema):
    total_groups: int
    active_groups: int
    inactive_groups: int
    total_members: int
    average_members_per_group: float
    group_type_distribution: Dict[str, int]

class FocusGroupList(BaseSchema):
    items: List[FocusGroup]
    total: int
    skip: int
    limit: int

class FocusGroupResponse(FocusGroup):
    pass

class FocusGroupUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    group_type: Optional[str] = None
    department_id: Optional[uuid.UUID] = None
    criteria: Optional[str] = None
    is_active: Optional[bool] = None

# Focus Group Members
class FocusGroupMemberBase(BaseSchema):
    employee_id: uuid.UUID
    role: str = Field(default="member", pattern="^(member|coordinator|leader)$")
    notes: Optional[str] = None

class FocusGroupMemberCreate(FocusGroupMemberBase):
    pass

class FocusGroupMemberResponse(FocusGroupMemberBase):
    id: uuid.UUID
    focus_group_id: uuid.UUID
    added_by: uuid.UUID
    joined_at: datetime

# Outlier Detection
class EmployeeOutlierInfo(BaseSchema):
    employee_id: uuid.UUID
    employee_name: str
    score: float
    z_score: float
    deviation_type: str = Field(..., pattern="^(low|high)$")
    confidence_level: float

class OutlierDetectionResult(BaseSchema):
    outliers: List[EmployeeOutlierInfo]
    total_outliers: int
    threshold_used: float
    detection_criteria: str
    detected_at: datetime

# =============================================================================
# KPI MEASUREMENT SCHEMAS (Missing)
# =============================================================================

class KPIMeasurementBase(BaseSchema):
    value: float
    measurement_date: Optional[datetime] = None
    notes: Optional[str] = None

class KPIMeasurementCreate(KPIMeasurementBase):
    pass

class KPIMeasurementUpdate(BaseSchema):
    value: Optional[float] = None
    measurement_date: Optional[datetime] = None
    notes: Optional[str] = None

class KPIMeasurement(KPIMeasurementBase):
    id: uuid.UUID
    kpi_id: uuid.UUID
    recorded_by: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True 