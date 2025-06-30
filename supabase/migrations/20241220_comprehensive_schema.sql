-- =====================================================
-- COMPREHENSIVE HR DASHBOARD SCHEMA MIGRATION
-- Implements Golden Flow & PRD Requirements
-- =====================================================

-- Drop existing triggers to avoid conflicts
DROP TRIGGER IF EXISTS update_departments_updated_at ON departments;
DROP TRIGGER IF EXISTS update_employees_updated_at ON employees;
DROP TRIGGER IF EXISTS update_performance_reviews_updated_at ON performance_reviews;
DROP TRIGGER IF EXISTS update_performance_goals_updated_at ON performance_goals;

-- =====================================================
-- EXTEND EXISTING TABLES
-- =====================================================

-- Add missing columns to employees table
ALTER TABLE employees 
ADD COLUMN IF NOT EXISTS first_name TEXT,
ADD COLUMN IF NOT EXISTS last_name TEXT,
ADD COLUMN IF NOT EXISTS phone TEXT,
ADD COLUMN IF NOT EXISTS manager_id UUID REFERENCES employees(id),
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS profile_data JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS skills JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS competencies JSONB DEFAULT '{}';

-- Add missing columns to departments table  
ALTER TABLE departments
ADD COLUMN IF NOT EXISTS description TEXT,
ADD COLUMN IF NOT EXISTS manager_id UUID REFERENCES employees(id);

-- Add missing columns to surveys table
ALTER TABLE surveys
ADD COLUMN IF NOT EXISTS start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS is_anonymous BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS target_departments JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS target_employees JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS frequency TEXT DEFAULT 'one-time',
ADD COLUMN IF NOT EXISTS platform_integrations JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW());

-- =====================================================
-- CORE SYSTEM TABLES
-- =====================================================

-- Users table (for authentication and user management)
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT,
    role TEXT NOT NULL DEFAULT 'employee', -- admin, hr_admin, manager, employee
    is_active BOOLEAN DEFAULT true,
    employee_id UUID REFERENCES employees(id),
    last_login TIMESTAMP WITH TIME ZONE,
    profile_settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- =====================================================
-- KPI MANAGEMENT SYSTEM (Golden Flow Step 1)
-- =====================================================

-- KPI Categories table
CREATE TABLE IF NOT EXISTS kpi_categories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    icon TEXT,
    color TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- KPIs table
CREATE TABLE IF NOT EXISTS kpis (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category_id UUID REFERENCES kpi_categories(id),
    target_value NUMERIC,
    current_value NUMERIC DEFAULT 0,
    unit TEXT,
    measurement_frequency TEXT NOT NULL, -- daily, weekly, monthly, quarterly, yearly
    calculation_method TEXT, -- manual, automatic, survey_based
    is_custom BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    target_departments JSONB DEFAULT '[]',
    target_employee_groups JSONB DEFAULT '[]',
    alert_threshold_low NUMERIC,
    alert_threshold_high NUMERIC,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW') NOT NULL
);

-- KPI Values table (for tracking historical data)
CREATE TABLE IF NOT EXISTS kpi_values (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    kpi_id UUID REFERENCES kpis(id) ON DELETE CASCADE,
    value NUMERIC NOT NULL,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    department_id UUID REFERENCES departments(id),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- =====================================================
-- ENHANCED SURVEY SYSTEM (Golden Flow Step 2)
-- =====================================================

-- Survey Templates table
CREATE TABLE IF NOT EXISTS survey_templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT, -- pulse, baseline, custom, performance, exit
    questions JSONB NOT NULL,
    is_predefined BOOLEAN DEFAULT false,
    tags JSONB DEFAULT '[]',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Survey Responses table
CREATE TABLE IF NOT EXISTS survey_responses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    survey_id UUID REFERENCES surveys(id) ON DELETE CASCADE,
    employee_id UUID REFERENCES employees(id) ON DELETE CASCADE,
    responses JSONB NOT NULL,
    completion_time_seconds INTEGER,
    is_anonymous BOOLEAN DEFAULT false,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    metadata JSONB DEFAULT '{}'
);

-- Survey KPI Mappings (link surveys to KPIs)
CREATE TABLE IF NOT EXISTS survey_kpi_mappings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    survey_id UUID REFERENCES surveys(id) ON DELETE CASCADE,
    kpi_id UUID REFERENCES kpis(id) ON DELETE CASCADE,
    question_mapping JSONB NOT NULL, -- maps survey questions to KPI calculation
    weight NUMERIC DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- =====================================================
-- FOCUS GROUPS & CLUSTERING (Golden Flow Step 4)
-- =====================================================

-- Focus Groups table
CREATE TABLE IF NOT EXISTS focus_groups (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL, -- department, role, performance, survey_based, custom
    criteria JSONB NOT NULL, -- selection criteria
    members JSONB NOT NULL, -- array of employee IDs
    status TEXT DEFAULT 'active', -- active, archived, dissolved
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Outliers table (for identifying problem areas)
CREATE TABLE IF NOT EXISTS outliers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    employee_id UUID REFERENCES employees(id) ON DELETE CASCADE,
    type TEXT NOT NULL, -- kpi_based, survey_based, performance_based
    category TEXT NOT NULL, -- engagement, stress, performance, attendance
    severity TEXT NOT NULL, -- low, medium, high, critical
    metrics JSONB NOT NULL, -- specific metrics that flagged this outlier
    contributing_factors JSONB DEFAULT '[]',
    is_resolved BOOLEAN DEFAULT false,
    focus_group_id UUID REFERENCES focus_groups(id),
    identified_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- ACTION PLANS SYSTEM (Golden Flow Step 4)
-- =====================================================

-- Action Plan Templates table (AI-generated and predefined)
CREATE TABLE IF NOT EXISTS action_plan_templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL, -- engagement, performance, stress, turnover, etc.
    steps JSONB NOT NULL, -- array of action steps
    estimated_duration_days INTEGER,
    success_metrics JSONB DEFAULT '[]',
    is_ai_generated BOOLEAN DEFAULT false,
    effectiveness_score NUMERIC, -- based on historical data
    tags JSONB DEFAULT '[]',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Action Plans table (actual implementations)
CREATE TABLE IF NOT EXISTS action_plans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    template_id UUID REFERENCES action_plan_templates(id),
    title TEXT NOT NULL,
    description TEXT,
    target_focus_group_id UUID REFERENCES focus_groups(id),
    target_departments JSONB DEFAULT '[]',
    target_employees JSONB DEFAULT '[]',
    target_kpis JSONB DEFAULT '[]', -- KPIs this action plan aims to improve
    status TEXT DEFAULT 'planned', -- planned, in_progress, completed, paused, cancelled
    priority TEXT DEFAULT 'medium', -- low, medium, high, critical
    start_date DATE,
    end_date DATE,
    actual_start_date DATE,
    actual_end_date DATE,
    assigned_to UUID REFERENCES users(id), -- responsible person
    stakeholders JSONB DEFAULT '[]', -- array of user IDs
    milestones JSONB DEFAULT '[]',
    progress_percentage INTEGER DEFAULT 0,
    budget NUMERIC,
    resources_required JSONB DEFAULT '[]',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Action Plan Progress table
CREATE TABLE IF NOT EXISTS action_plan_progress (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    action_plan_id UUID REFERENCES action_plans(id) ON DELETE CASCADE,
    milestone_name TEXT NOT NULL,
    status TEXT NOT NULL, -- not_started, in_progress, completed, blocked
    progress_percentage INTEGER DEFAULT 0,
    notes TEXT,
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- =====================================================
-- EFFICACY MEASUREMENT (Golden Flow Step 5)
-- =====================================================

-- Efficacy Measurements table
CREATE TABLE IF NOT EXISTS efficacy_measurements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    action_plan_id UUID REFERENCES action_plans(id) ON DELETE CASCADE,
    measurement_type TEXT NOT NULL, -- baseline, interim, final
    kpi_id UUID REFERENCES kpis(id),
    baseline_value NUMERIC,
    measured_value NUMERIC,
    improvement_percentage NUMERIC,
    improvement_absolute NUMERIC,
    statistical_significance NUMERIC,
    measurement_date TIMESTAMP WITH TIME ZONE NOT NULL,
    survey_id UUID REFERENCES surveys(id), -- if measurement came from survey
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- =====================================================
-- PERFORMANCE MANAGEMENT SYSTEM
-- =====================================================

-- Performance Review Cycles table
CREATE TABLE IF NOT EXISTS performance_review_cycles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL, -- annual, quarterly, monthly, project_based
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status TEXT DEFAULT 'planning', -- planning, active, review, completed
    departments JSONB DEFAULT '[]', -- target departments
    template_config JSONB DEFAULT '{}',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Update performance_reviews to link to cycles
ALTER TABLE performance_reviews 
ADD COLUMN IF NOT EXISTS cycle_id UUID REFERENCES performance_review_cycles(id),
ADD COLUMN IF NOT EXISTS self_assessment JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS peer_feedback JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS manager_feedback JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS goals_for_next_period JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS calibration_score NUMERIC,
ADD COLUMN IF NOT EXISTS review_type TEXT DEFAULT 'annual';

-- 1:1 Meetings table
CREATE TABLE IF NOT EXISTS one_on_one_meetings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    employee_id UUID REFERENCES employees(id) ON DELETE CASCADE,
    manager_id UUID REFERENCES employees(id) ON DELETE CASCADE,
    scheduled_date TIMESTAMP WITH TIME ZONE NOT NULL,
    actual_date TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER,
    agenda JSONB DEFAULT '[]',
    notes TEXT,
    action_items JSONB DEFAULT '[]',
    status TEXT DEFAULT 'scheduled', -- scheduled, completed, cancelled, rescheduled
    meeting_type TEXT DEFAULT 'regular', -- regular, performance, career, project
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Feedback table (360-degree feedback)
CREATE TABLE IF NOT EXISTS feedback (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    recipient_id UUID REFERENCES employees(id) ON DELETE CASCADE,
    giver_id UUID REFERENCES employees(id) ON DELETE CASCADE,
    feedback_type TEXT NOT NULL, -- peer, upward, downward, self
    category TEXT, -- performance, behavior, skills, communication
    content TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    is_anonymous BOOLEAN DEFAULT false,
    related_review_id UUID REFERENCES performance_reviews(id),
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Praise and Recognition table
CREATE TABLE IF NOT EXISTS praise_recognition (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    recipient_id UUID REFERENCES employees(id) ON DELETE CASCADE,
    giver_id UUID REFERENCES employees(id) ON DELETE CASCADE,
    type TEXT NOT NULL, -- praise, recognition, achievement
    title TEXT NOT NULL,
    description TEXT,
    category TEXT, -- teamwork, innovation, leadership, achievement
    visibility TEXT DEFAULT 'team', -- private, team, department, company
    platform_posted JSONB DEFAULT '[]', -- which platforms this was posted to
    reactions JSONB DEFAULT '{}', -- likes, comments, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW') NOT NULL
);

-- =====================================================
-- PLATFORM INTEGRATIONS
-- =====================================================

-- Integration Configurations table
CREATE TABLE IF NOT EXISTS integration_configs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    platform TEXT NOT NULL, -- slack, teams, zoom, email
    config_data JSONB NOT NULL, -- platform-specific configuration
    is_active BOOLEAN DEFAULT true,
    department_id UUID REFERENCES departments(id), -- can be department-specific
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Notification Queue table
CREATE TABLE IF NOT EXISTS notification_queue (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    recipient_id UUID REFERENCES users(id),
    type TEXT NOT NULL, -- survey_invitation, reminder, alert, praise, feedback_request
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    platform TEXT NOT NULL, -- slack, teams, email, in_app
    status TEXT DEFAULT 'pending', -- pending, sent, failed, cancelled
    scheduled_for TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sent_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- =====================================================
-- ANALYTICS & REPORTING
-- =====================================================

-- Analytics Events table (for tracking user interactions)
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    event_type TEXT NOT NULL,
    event_data JSONB NOT NULL,
    session_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Dashboard Configurations table (for custom dashboards)
CREATE TABLE IF NOT EXISTS dashboard_configs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    layout JSONB NOT NULL,
    widgets JSONB NOT NULL,
    is_default BOOLEAN DEFAULT false,
    is_shared BOOLEAN DEFAULT false,
    shared_with JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- =====================================================
-- ROW LEVEL SECURITY POLICIES
-- =====================================================

-- Enable RLS on all new tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE kpi_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE kpis ENABLE ROW LEVEL SECURITY;
ALTER TABLE kpi_values ENABLE ROW LEVEL SECURITY;
ALTER TABLE survey_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE survey_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE survey_kpi_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE focus_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE outliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_plan_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_plan_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE efficacy_measurements ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_review_cycles ENABLE ROW LEVEL SECURITY;
ALTER TABLE one_on_one_meetings ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE praise_recognition ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE dashboard_configs ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- CREATE COMPREHENSIVE RLS POLICIES
-- =====================================================

-- Users policies
CREATE POLICY "Users can read their own data" ON users FOR SELECT USING (auth.uid()::text = id::text);
CREATE POLICY "HR Admins can read all users" ON users FOR SELECT USING (
    EXISTS (SELECT 1 FROM users WHERE id::text = auth.uid()::text AND role IN ('admin', 'hr_admin'))
);

-- KPIs policies  
CREATE POLICY "All authenticated users can read KPIs" ON kpis FOR SELECT TO authenticated USING (true);
CREATE POLICY "HR Admins can manage KPIs" ON kpis FOR ALL TO authenticated USING (
    EXISTS (SELECT 1 FROM users WHERE id::text = auth.uid()::text AND role IN ('admin', 'hr_admin'))
);

-- Survey responses policies
CREATE POLICY "Users can read their own survey responses" ON survey_responses FOR SELECT USING (
    employee_id IN (SELECT id FROM employees WHERE employees.id IN (SELECT employee_id FROM users WHERE id::text = auth.uid()::text))
);
CREATE POLICY "HR Admins can read all survey responses" ON survey_responses FOR SELECT USING (
    EXISTS (SELECT 1 FROM users WHERE id::text = auth.uid()::text AND role IN ('admin', 'hr_admin'))
);

-- Action plans policies
CREATE POLICY "All authenticated users can read action plans" ON action_plans FOR SELECT TO authenticated USING (true);
CREATE POLICY "HR Admins and Managers can manage action plans" ON action_plans FOR ALL TO authenticated USING (
    EXISTS (SELECT 1 FROM users WHERE id::text = auth.uid()::text AND role IN ('admin', 'hr_admin', 'manager'))
);

-- =====================================================
-- CREATE UPDATED TIMESTAMP TRIGGERS
-- =====================================================

-- Recreate the update timestamp function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all tables with updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_kpis_updated_at BEFORE UPDATE ON kpis FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_surveys_updated_at BEFORE UPDATE ON surveys FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_survey_templates_updated_at BEFORE UPDATE ON survey_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_focus_groups_updated_at BEFORE UPDATE ON focus_groups FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_action_plan_templates_updated_at BEFORE UPDATE ON action_plan_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_action_plans_updated_at BEFORE UPDATE ON action_plans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_action_plan_progress_updated_at BEFORE UPDATE ON action_plan_progress FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_performance_review_cycles_updated_at BEFORE UPDATE ON performance_review_cycles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_one_on_one_meetings_updated_at BEFORE UPDATE ON one_on_one_meetings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_integration_configs_updated_at BEFORE UPDATE ON integration_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_dashboard_configs_updated_at BEFORE UPDATE ON dashboard_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Recreate original triggers
CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON departments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON employees FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_performance_reviews_updated_at BEFORE UPDATE ON performance_reviews FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_performance_goals_updated_at BEFORE UPDATE ON performance_goals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- INSERT INITIAL DATA
-- =====================================================

-- Insert predefined KPI categories
INSERT INTO kpi_categories (name, description, icon, color) VALUES
('Employee Engagement', 'Measures how engaged and motivated employees are', 'users', '#3B82F6'),
('Performance', 'Tracks individual and team performance metrics', 'trending-up', '#10B981'),
('Retention', 'Monitors employee turnover and retention rates', 'user-check', '#F59E0B'),
('Training & Development', 'Tracks learning and development effectiveness', 'book-open', '#8B5CF6'),
('Diversity & Inclusion', 'Measures diversity and inclusion metrics', 'globe', '#EF4444'),
('Well-being', 'Monitors employee health and well-being', 'heart', '#EC4899'),
('Productivity', 'Tracks productivity and efficiency metrics', 'zap', '#6366F1'),
('Communication', 'Measures communication effectiveness', 'message-circle', '#14B8A6')
ON CONFLICT (name) DO NOTHING;

-- Insert predefined KPIs
INSERT INTO kpis (name, description, category_id, unit, measurement_frequency, calculation_method, is_custom) 
SELECT 
    kpi.name,
    kpi.description,
    cat.id,
    kpi.unit,
    kpi.frequency,
    kpi.method,
    false
FROM (VALUES
    ('Employee Engagement Score', 'Overall engagement score from surveys', 'Employee Engagement', '%', 'monthly', 'survey_based'),
    ('Employee Net Promoter Score (eNPS)', 'Likelihood of employees recommending the company', 'Employee Engagement', 'score', 'quarterly', 'survey_based'),
    ('Turnover Rate', 'Percentage of employees who left the company', 'Retention', '%', 'monthly', 'automatic'),
    ('Voluntary Turnover Rate', 'Percentage of employees who voluntarily left', 'Retention', '%', 'monthly', 'automatic'),
    ('Time to Fill Positions', 'Average days to fill open positions', 'Performance', 'days', 'monthly', 'automatic'),
    ('Training Completion Rate', 'Percentage of required training completed', 'Training & Development', '%', 'monthly', 'automatic'),
    ('Training Effectiveness Score', 'Effectiveness of training programs', 'Training & Development', 'score', 'quarterly', 'survey_based'),
    ('Diversity Ratio', 'Ratio of diverse employees in the organization', 'Diversity & Inclusion', '%', 'quarterly', 'automatic'),
    ('Pay Equity Ratio', 'Gender pay gap measurement', 'Diversity & Inclusion', '%', 'annually', 'manual'),
    ('Stress Level Index', 'Average stress level reported by employees', 'Well-being', 'score', 'monthly', 'survey_based'),
    ('Work-Life Balance Score', 'Employee satisfaction with work-life balance', 'Well-being', 'score', 'quarterly', 'survey_based'),
    ('Productivity Index', 'Overall productivity measurement', 'Productivity', 'score', 'monthly', 'automatic'),
    ('Absenteeism Rate', 'Percentage of unplanned absences', 'Performance', '%', 'monthly', 'automatic'),
    ('Internal Communication Effectiveness', 'Effectiveness of internal communications', 'Communication', 'score', 'quarterly', 'survey_based')
) AS kpi(name, description, category, unit, frequency, method)
JOIN kpi_categories cat ON cat.name = kpi.category
ON CONFLICT (name) DO NOTHING;

-- Insert survey templates
INSERT INTO survey_templates (name, description, category, questions, is_predefined) VALUES
('Employee Engagement Pulse', 'Quick 5-question engagement survey', 'pulse', 
 '[{"id": 1, "text": "How satisfied are you with your current role?", "type": "scale", "scale": 5}, 
   {"id": 2, "text": "How likely are you to recommend this company as a place to work?", "type": "scale", "scale": 10},
   {"id": 3, "text": "Do you feel your work has meaning and purpose?", "type": "scale", "scale": 5},
   {"id": 4, "text": "How well does your manager support your professional development?", "type": "scale", "scale": 5},
   {"id": 5, "text": "What one thing would improve your work experience?", "type": "text"}]', 
 true),
('Stress & Well-being Check', 'Survey to assess employee stress levels', 'pulse',
 '[{"id": 1, "text": "How would you rate your current stress level at work?", "type": "scale", "scale": 5},
   {"id": 2, "text": "How manageable is your current workload?", "type": "scale", "scale": 5},
   {"id": 3, "text": "How satisfied are you with your work-life balance?", "type": "scale", "scale": 5},
   {"id": 4, "text": "Do you feel you have adequate support from your team?", "type": "boolean"},
   {"id": 5, "text": "What support would help reduce your stress?", "type": "text"}]',
 true)
ON CONFLICT DO NOTHING;

-- Insert action plan templates
INSERT INTO action_plan_templates (title, description, category, steps, estimated_duration_days, is_ai_generated) VALUES
('Team Building Workshop', 'Improve team cohesion and collaboration', 'engagement',
 '[{"step": 1, "title": "Plan workshop activities", "duration": 3, "responsible": "HR"},
   {"step": 2, "title": "Book venue and facilitator", "duration": 5, "responsible": "HR"},
   {"step": 3, "title": "Conduct team building workshop", "duration": 1, "responsible": "Manager"},
   {"step": 4, "title": "Follow-up survey", "duration": 7, "responsible": "HR"}]',
 30, false),
('Stress Reduction Program', 'Implement strategies to reduce workplace stress', 'stress',
 '[{"step": 1, "title": "Assess current stress factors", "duration": 7, "responsible": "Manager"},
   {"step": 2, "title": "Implement flexible work arrangements", "duration": 14, "responsible": "HR"},
   {"step": 3, "title": "Provide stress management training", "duration": 21, "responsible": "HR"},
   {"step": 4, "title": "Monitor stress levels", "duration": 30, "responsible": "Manager"}]',
 60, false)
ON CONFLICT DO NOTHING;

-- =====================================================
-- CREATE USEFUL VIEWS
-- =====================================================

-- Employee summary view
CREATE OR REPLACE VIEW employee_summary AS
SELECT 
    e.id,
    e.first_name,
    e.last_name,
    e.email,
    e.position,
    d.name as department_name,
    e.hire_date,
    e.status,
    e.is_active,
    m.first_name || ' ' || m.last_name as manager_name,
    u.role as user_role
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id
LEFT JOIN employees m ON e.manager_id = m.id
LEFT JOIN users u ON u.employee_id = e.id;

-- KPI Dashboard view
CREATE OR REPLACE VIEW kpi_dashboard AS
SELECT 
    k.id,
    k.name,
    k.description,
    k.current_value,
    k.target_value,
    k.unit,
    kc.name as category_name,
    kc.color as category_color,
    CASE 
        WHEN k.target_value > 0 THEN ROUND((k.current_value / k.target_value * 100)::numeric, 2)
        ELSE 0
    END as achievement_percentage,
    k.measurement_frequency,
    k.is_active
FROM kpis k
JOIN kpi_categories kc ON k.category_id = kc.id
WHERE k.is_active = true;

-- Action Plan Status view
CREATE OR REPLACE VIEW action_plan_status AS
SELECT 
    ap.id,
    ap.title,
    ap.status,
    ap.priority,
    ap.progress_percentage,
    ap.start_date,
    ap.end_date,
    fg.name as focus_group_name,
    u.email as assigned_to_email,
    creator.email as created_by_email,
    COUNT(apr.id) as total_milestones,
    COUNT(CASE WHEN apr.status = 'completed' THEN 1 END) as completed_milestones
FROM action_plans ap
LEFT JOIN focus_groups fg ON ap.target_focus_group_id = fg.id
LEFT JOIN users u ON ap.assigned_to = u.id
LEFT JOIN users creator ON ap.created_by = creator.id
LEFT JOIN action_plan_progress apr ON ap.id = apr.action_plan_id
GROUP BY ap.id, ap.title, ap.status, ap.priority, ap.progress_percentage, 
         ap.start_date, ap.end_date, fg.name, u.email, creator.email;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Critical indexes for performance
CREATE INDEX IF NOT EXISTS idx_employees_department_id ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_employees_manager_id ON employees(manager_id);
CREATE INDEX IF NOT EXISTS idx_survey_responses_survey_id ON survey_responses(survey_id);
CREATE INDEX IF NOT EXISTS idx_survey_responses_employee_id ON survey_responses(employee_id);
CREATE INDEX IF NOT EXISTS idx_kpi_values_kpi_id ON kpi_values(kpi_id);
CREATE INDEX IF NOT EXISTS idx_kpi_values_period_start ON kpi_values(period_start);
CREATE INDEX IF NOT EXISTS idx_action_plans_status ON action_plans(status);
CREATE INDEX IF NOT EXISTS idx_focus_groups_type ON focus_groups(type);
CREATE INDEX IF NOT EXISTS idx_outliers_employee_id ON outliers(employee_id);
CREATE INDEX IF NOT EXISTS idx_outliers_severity ON outliers(severity);
CREATE INDEX IF NOT EXISTS idx_efficacy_measurements_action_plan_id ON efficacy_measurements(action_plan_id);
CREATE INDEX IF NOT EXISTS idx_notification_queue_status ON notification_queue(status);
CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_created_at ON analytics_events(created_at);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_survey_responses_survey_employee ON survey_responses(survey_id, employee_id);
CREATE INDEX IF NOT EXISTS idx_kpi_values_kpi_period ON kpi_values(kpi_id, period_start);
CREATE INDEX IF NOT EXISTS idx_action_plans_status_priority ON action_plans(status, priority);

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================
-- Migration completed successfully!
-- This schema supports the complete Golden Flow and PRD requirements 