from sqlalchemy import Boolean, Column, ForeignKey, String, DateTime, Float, JSON, Text, Integer, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid

# =====================================================
# CORE SYSTEM MODELS
# =====================================================

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String)
    role = Column(String, default='employee', nullable=False)  # admin, hr_admin, manager, employee
    is_active = Column(Boolean, default=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    last_login = Column(DateTime(timezone=True))
    profile_settings = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="user")

class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")
    manager = relationship("Employee", foreign_keys=[manager_id], post_update=True)

class Employee(Base):
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    first_name = Column(String)
    last_name = Column(String)
    name = Column(String, nullable=False)  # Full name for compatibility
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    manager_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    position = Column(String, nullable=False)
    hire_date = Column(Date, nullable=False)
    status = Column(String, default='active', nullable=False)
    is_active = Column(Boolean, default=True)
    profile_data = Column(JSON, default={})
    skills = Column(JSON, default=[])
    competencies = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="employee")
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    manager = relationship("Employee", remote_side=[id], foreign_keys=[manager_id], post_update=True)
    performance_reviews = relationship("PerformanceReview", back_populates="employee", foreign_keys="PerformanceReview.employee_id")
    survey_responses = relationship("SurveyResponse", back_populates="employee")
    feedback_given = relationship("Feedback", back_populates="giver", foreign_keys="Feedback.giver_id")
    feedback_received = relationship("Feedback", back_populates="recipient", foreign_keys="Feedback.recipient_id")

# =====================================================
# KPI MANAGEMENT MODELS
# =====================================================

class KPICategory(Base):
    __tablename__ = "kpi_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    icon = Column(String)
    color = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    kpis = relationship("KPI", back_populates="category")

class KPI(Base):
    __tablename__ = "kpis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category_id = Column(UUID(as_uuid=True), ForeignKey("kpi_categories.id"))
    target_value = Column(Numeric)
    current_value = Column(Numeric, default=0)
    unit = Column(String)
    measurement_frequency = Column(String, nullable=False)  # daily, weekly, monthly, quarterly, yearly
    calculation_method = Column(String)  # manual, automatic, survey_based
    is_custom = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    target_departments = Column(JSON, default=[])
    target_employee_groups = Column(JSON, default=[])
    alert_threshold_low = Column(Numeric)
    alert_threshold_high = Column(Numeric)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    category = relationship("KPICategory", back_populates="kpis")
    values = relationship("KPIValue", back_populates="kpi")
    creator = relationship("User")

class KPIValue(Base):
    __tablename__ = "kpi_values"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    kpi_id = Column(UUID(as_uuid=True), ForeignKey("kpis.id", ondelete="CASCADE"))
    value = Column(Numeric, nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    extra_metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    kpi = relationship("KPI", back_populates="values")
    department = relationship("Department")

# =====================================================
# SURVEY SYSTEM MODELS
# =====================================================

class SurveyTemplate(Base):
    __tablename__ = "survey_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)  # pulse, baseline, custom, performance, exit
    questions = Column(JSON, nullable=False)
    is_predefined = Column(Boolean, default=False)
    tags = Column(JSON, default=[])
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    creator = relationship("User")

class Survey(Base):
    __tablename__ = "surveys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String, nullable=False)
    status = Column(String, default='draft', nullable=False)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=False)
    is_anonymous = Column(Boolean, default=False)
    target_departments = Column(JSON, default=[])
    target_employees = Column(JSON, default=[])
    frequency = Column(String, default='one-time')
    platform_integrations = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    questions = relationship("SurveyQuestion", back_populates="survey")
    responses = relationship("SurveyResponse", back_populates="survey")
    kpi_mappings = relationship("SurveyKPIMapping", back_populates="survey")

class SurveyQuestion(Base):
    __tablename__ = "survey_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    survey_id = Column(UUID(as_uuid=True), ForeignKey("surveys.id", ondelete="CASCADE"))
    text = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    options = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    survey = relationship("Survey", back_populates="questions")

class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    survey_id = Column(UUID(as_uuid=True), ForeignKey("surveys.id", ondelete="CASCADE"))
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"))
    responses = Column(JSON, nullable=False)
    completion_time_seconds = Column(Integer)
    is_anonymous = Column(Boolean, default=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    extra_metadata = Column(JSON, default={})

    # Relationships
    survey = relationship("Survey", back_populates="responses")
    employee = relationship("Employee", back_populates="survey_responses")

class SurveyKPIMapping(Base):
    __tablename__ = "survey_kpi_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    survey_id = Column(UUID(as_uuid=True), ForeignKey("surveys.id", ondelete="CASCADE"))
    kpi_id = Column(UUID(as_uuid=True), ForeignKey("kpis.id", ondelete="CASCADE"))
    question_mapping = Column(JSON, nullable=False)
    weight = Column(Numeric, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    survey = relationship("Survey", back_populates="kpi_mappings")
    kpi = relationship("KPI")

# =====================================================
# FOCUS GROUPS & OUTLIER MODELS
# =====================================================

class FocusGroup(Base):
    __tablename__ = "focus_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String, nullable=False)  # department, role, performance, survey_based, custom
    criteria = Column(JSON, nullable=False)
    members = Column(JSON, nullable=False)  # array of employee IDs
    status = Column(String, default='active')  # active, archived, dissolved
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    creator = relationship("User")
    action_plans = relationship("ActionPlan", back_populates="target_focus_group")

class Outlier(Base):
    __tablename__ = "outliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"))
    type = Column(String, nullable=False)  # kpi_based, survey_based, performance_based
    category = Column(String, nullable=False)  # engagement, stress, performance, attendance
    severity = Column(String, nullable=False)  # low, medium, high, critical
    metrics = Column(JSON, nullable=False)
    contributing_factors = Column(JSON, default=[])
    is_resolved = Column(Boolean, default=False)
    focus_group_id = Column(UUID(as_uuid=True), ForeignKey("focus_groups.id"))
    identified_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))

    # Relationships
    employee = relationship("Employee")
    focus_group = relationship("FocusGroup")

# =====================================================
# ACTION PLAN MODELS
# =====================================================

class ActionPlanTemplate(Base):
    __tablename__ = "action_plan_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False)
    steps = Column(JSON, nullable=False)
    estimated_duration_days = Column(Integer)
    success_metrics = Column(JSON, default=[])
    is_ai_generated = Column(Boolean, default=False)
    effectiveness_score = Column(Numeric)
    tags = Column(JSON, default=[])
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    creator = relationship("User")

class ActionPlan(Base):
    __tablename__ = "action_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("action_plan_templates.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    target_focus_group_id = Column(UUID(as_uuid=True), ForeignKey("focus_groups.id"))
    target_departments = Column(JSON, default=[])
    target_employees = Column(JSON, default=[])
    target_kpis = Column(JSON, default=[])
    status = Column(String, default='planned')  # planned, in_progress, completed, paused, cancelled
    priority = Column(String, default='medium')  # low, medium, high, critical
    start_date = Column(Date)
    end_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    stakeholders = Column(JSON, default=[])
    milestones = Column(JSON, default=[])
    progress_percentage = Column(Integer, default=0)
    budget = Column(Numeric)
    resources_required = Column(JSON, default=[])
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    template = relationship("ActionPlanTemplate")
    target_focus_group = relationship("FocusGroup", back_populates="action_plans")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])
    progress_updates = relationship("ActionPlanProgress", back_populates="action_plan")
    efficacy_measurements = relationship("EfficacyMeasurement", back_populates="action_plan")

class ActionPlanProgress(Base):
    __tablename__ = "action_plan_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    action_plan_id = Column(UUID(as_uuid=True), ForeignKey("action_plans.id", ondelete="CASCADE"))
    milestone_name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # not_started, in_progress, completed, blocked
    progress_percentage = Column(Integer, default=0)
    notes = Column(Text)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    action_plan = relationship("ActionPlan", back_populates="progress_updates")
    updater = relationship("User")

# =====================================================
# EFFICACY MEASUREMENT MODEL
# =====================================================

class EfficacyMeasurement(Base):
    __tablename__ = "efficacy_measurements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    action_plan_id = Column(UUID(as_uuid=True), ForeignKey("action_plans.id", ondelete="CASCADE"))
    measurement_type = Column(String, nullable=False)  # baseline, interim, final
    kpi_id = Column(UUID(as_uuid=True), ForeignKey("kpis.id"))
    baseline_value = Column(Numeric)
    measured_value = Column(Numeric)
    improvement_percentage = Column(Numeric)
    improvement_absolute = Column(Numeric)
    statistical_significance = Column(Numeric)
    measurement_date = Column(DateTime(timezone=True), nullable=False)
    survey_id = Column(UUID(as_uuid=True), ForeignKey("surveys.id"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    action_plan = relationship("ActionPlan", back_populates="efficacy_measurements")
    kpi = relationship("KPI")
    survey = relationship("Survey")

# =====================================================
# PERFORMANCE MANAGEMENT MODELS
# =====================================================

class PerformanceReviewCycle(Base):
    __tablename__ = "performance_review_cycles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String, nullable=False)  # annual, quarterly, monthly, project_based
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String, default='planning')  # planning, active, review, completed
    departments = Column(JSON, default=[])
    template_config = Column(JSON, default={})
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    creator = relationship("User")
    reviews = relationship("PerformanceReview", back_populates="cycle")

class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"))
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"))
    cycle_id = Column(UUID(as_uuid=True), ForeignKey("performance_review_cycles.id"))
    rating = Column(Integer, nullable=False)  # 1-5 scale
    comments = Column(Text)
    status = Column(String, default='pending', nullable=False)
    self_assessment = Column(JSON, default={})
    peer_feedback = Column(JSON, default=[])
    manager_feedback = Column(JSON, default={})
    goals_for_next_period = Column(JSON, default=[])
    calibration_score = Column(Numeric)
    review_type = Column(String, default='annual')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="performance_reviews", foreign_keys=[employee_id])
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])
    cycle = relationship("PerformanceReviewCycle", back_populates="reviews")
    goals = relationship("PerformanceGoal", back_populates="review")

class PerformanceGoal(Base):
    __tablename__ = "performance_goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    review_id = Column(UUID(as_uuid=True), ForeignKey("performance_reviews.id", ondelete="CASCADE"))
    description = Column(Text, nullable=False)
    status = Column(String, default='pending', nullable=False)
    due_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    review = relationship("PerformanceReview", back_populates="goals")

class OneOnOneMeeting(Base):
    __tablename__ = "one_on_one_meetings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"))
    manager_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"))
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    actual_date = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    agenda = Column(JSON, default=[])
    notes = Column(Text)
    action_items = Column(JSON, default=[])
    status = Column(String, default='scheduled')  # scheduled, completed, cancelled, rescheduled
    meeting_type = Column(String, default='regular')  # regular, performance, career, project
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    manager = relationship("Employee", foreign_keys=[manager_id])

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"))
    giver_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"))
    feedback_type = Column(String, nullable=False)  # peer, upward, downward, self
    category = Column(String)  # performance, behavior, skills, communication
    content = Column(Text, nullable=False)
    rating = Column(Integer)  # 1-5 scale
    is_anonymous = Column(Boolean, default=False)
    related_review_id = Column(UUID(as_uuid=True), ForeignKey("performance_reviews.id"))
    tags = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    recipient = relationship("Employee", back_populates="feedback_received", foreign_keys=[recipient_id])
    giver = relationship("Employee", back_populates="feedback_given", foreign_keys=[giver_id])
    related_review = relationship("PerformanceReview")

class PraiseRecognition(Base):
    __tablename__ = "praise_recognition"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"))
    giver_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"))
    type = Column(String, nullable=False)  # praise, recognition, achievement
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)  # teamwork, innovation, leadership, achievement
    visibility = Column(String, default='team')  # private, team, department, company
    platform_posted = Column(JSON, default=[])
    reactions = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    recipient = relationship("Employee", foreign_keys=[recipient_id])
    giver = relationship("Employee", foreign_keys=[giver_id])

# =====================================================
# SECURITY & COMPLIANCE MODELS
# =====================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String, nullable=False)  # login, data_export, survey_create, etc.
    details = Column(JSON, default={})  # Additional action details
    ip_address = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")

class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    consent_type = Column(String, nullable=False)  # data_processing, cookies, marketing
    purpose = Column(String, nullable=False)
    data_categories = Column(JSON, default=[])  # Types of data being processed
    consent_given = Column(Boolean, nullable=False)
    consent_text = Column(Text)  # The exact consent text shown to user
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))  # When consent expires
    
    # Relationships
    user = relationship("User")

class DataRetentionPolicy(Base):
    __tablename__ = "data_retention_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    data_type = Column(String, nullable=False)  # survey_responses, audit_logs, etc.
    retention_period_days = Column(Integer, nullable=False)
    auto_delete = Column(Boolean, default=False)
    legal_basis = Column(String)  # GDPR legal basis
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    creator = relationship("User") 