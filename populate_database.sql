-- =====================================================
-- COMPREHENSIVE DATABASE POPULATION SCRIPT
-- HR Management System - Sample Data
-- Run this in Supabase SQL Editor
-- =====================================================

-- Disable RLS temporarily for data insertion
SET session_replication_role = replica;

-- =====================================================
-- 1. DEPARTMENTS
-- =====================================================
INSERT INTO departments (id, name, description, created_at) VALUES
(gen_random_uuid(), 'Engineering', 'Software development and technical operations', NOW()),
(gen_random_uuid(), 'Marketing', 'Brand promotion and customer acquisition', NOW()),
(gen_random_uuid(), 'Sales', 'Revenue generation and client relations', NOW()),
(gen_random_uuid(), 'Human Resources', 'Employee management and organizational development', NOW()),
(gen_random_uuid(), 'Finance', 'Financial planning and accounting', NOW()),
(gen_random_uuid(), 'Operations', 'Business operations and process optimization', NOW()),
(gen_random_uuid(), 'Product', 'Product strategy and development', NOW()),
(gen_random_uuid(), 'Customer Success', 'Customer satisfaction and retention', NOW()),
(gen_random_uuid(), 'Legal', 'Legal compliance and risk management', NOW()),
(gen_random_uuid(), 'Design', 'UI/UX and visual design', NOW());

-- =====================================================
-- 2. EMPLOYEES
-- =====================================================
WITH dept_ids AS (
  SELECT id, name FROM departments
)
INSERT INTO employees (id, name, first_name, last_name, email, department_id, position, hire_date, status, phone, is_active) 
SELECT 
  gen_random_uuid(),
  emp.full_name,
  emp.first_name,
  emp.last_name,
  emp.email,
  dept_ids.id,
  emp.position,
  emp.hire_date::date,
  'active',
  emp.phone,
  true
FROM (VALUES
  -- Engineering Team
  ('John Smith', 'John', 'Smith', 'john.smith@company.com', 'Engineering', 'Senior Software Engineer', '2022-03-15', '+1-555-0101'),
  ('Sarah Johnson', 'Sarah', 'Johnson', 'sarah.johnson@company.com', 'Engineering', 'Engineering Manager', '2021-01-20', '+1-555-0102'),
  ('Michael Chen', 'Michael', 'Chen', 'michael.chen@company.com', 'Engineering', 'Full Stack Developer', '2023-06-10', '+1-555-0103'),
  ('Emily Davis', 'Emily', 'Davis', 'emily.davis@company.com', 'Engineering', 'DevOps Engineer', '2022-11-05', '+1-555-0104'),
  ('David Wilson', 'David', 'Wilson', 'david.wilson@company.com', 'Engineering', 'Frontend Developer', '2023-02-14', '+1-555-0105'),
  
  -- Marketing Team
  ('Jessica Brown', 'Jessica', 'Brown', 'jessica.brown@company.com', 'Marketing', 'Marketing Manager', '2021-08-12', '+1-555-0201'),
  ('Robert Taylor', 'Robert', 'Taylor', 'robert.taylor@company.com', 'Marketing', 'Content Marketing Specialist', '2022-09-03', '+1-555-0202'),
  ('Lisa Anderson', 'Lisa', 'Anderson', 'lisa.anderson@company.com', 'Marketing', 'Digital Marketing Coordinator', '2023-04-18', '+1-555-0203'),
  ('James Thomas', 'James', 'Thomas', 'james.thomas@company.com', 'Marketing', 'Brand Manager', '2022-07-22', '+1-555-0204'),
  
  -- Sales Team
  ('Amanda Martinez', 'Amanda', 'Martinez', 'amanda.martinez@company.com', 'Sales', 'Sales Director', '2020-05-08', '+1-555-0301'),
  ('Chris Garcia', 'Chris', 'Garcia', 'chris.garcia@company.com', 'Sales', 'Account Executive', '2022-12-01', '+1-555-0302'),
  ('Nicole Rodriguez', 'Nicole', 'Rodriguez', 'nicole.rodriguez@company.com', 'Sales', 'Sales Development Rep', '2023-08-15', '+1-555-0303'),
  ('Kevin Lee', 'Kevin', 'Lee', 'kevin.lee@company.com', 'Sales', 'Senior Account Manager', '2021-11-30', '+1-555-0304'),
  
  -- HR Team
  ('Rachel White', 'Rachel', 'White', 'rachel.white@company.com', 'Human Resources', 'HR Director', '2020-02-15', '+1-555-0401'),
  ('Mark Thompson', 'Mark', 'Thompson', 'mark.thompson@company.com', 'Human Resources', 'HR Business Partner', '2021-06-20', '+1-555-0402'),
  ('Jennifer Clark', 'Jennifer', 'Clark', 'jennifer.clark@company.com', 'Human Resources', 'Talent Acquisition Specialist', '2022-10-08', '+1-555-0403'),
  
  -- Finance Team
  ('Daniel Kim', 'Daniel', 'Kim', 'daniel.kim@company.com', 'Finance', 'Finance Director', '2019-09-12', '+1-555-0501'),
  ('Stephanie Hall', 'Stephanie', 'Hall', 'stephanie.hall@company.com', 'Finance', 'Financial Analyst', '2022-04-25', '+1-555-0502'),
  ('Andrew Lewis', 'Andrew', 'Lewis', 'andrew.lewis@company.com', 'Finance', 'Senior Accountant', '2021-12-10', '+1-555-0503'),
  
  -- Operations Team
  ('Michelle Young', 'Michelle', 'Young', 'michelle.young@company.com', 'Operations', 'Operations Manager', '2020-10-05', '+1-555-0601'),
  ('Brian Walker', 'Brian', 'Walker', 'brian.walker@company.com', 'Operations', 'Business Analyst', '2022-08-18', '+1-555-0602'),
  
  -- Product Team
  ('Anna Scott', 'Anna', 'Scott', 'anna.scott@company.com', 'Product', 'Product Manager', '2021-03-22', '+1-555-0701'),
  ('Ryan Green', 'Ryan', 'Green', 'ryan.green@company.com', 'Product', 'Product Designer', '2022-05-15', '+1-555-0702'),
  
  -- Customer Success Team
  ('Megan Adams', 'Megan', 'Adams', 'megan.adams@company.com', 'Customer Success', 'CS Manager', '2021-07-08', '+1-555-0801'),
  ('Tyler Baker', 'Tyler', 'Baker', 'tyler.baker@company.com', 'Customer Success', 'Customer Success Rep', '2023-01-12', '+1-555-0802'),
  
  -- Legal Team
  ('Laura Nelson', 'Laura', 'Nelson', 'laura.nelson@company.com', 'Legal', 'Legal Counsel', '2020-12-03', '+1-555-0901'),
  
  -- Design Team
  ('Alex Turner', 'Alex', 'Turner', 'alex.turner@company.com', 'Design', 'UX Designer', '2022-06-28', '+1-555-1001'),
  ('Samantha Phillips', 'Samantha', 'Phillips', 'samantha.phillips@company.com', 'Design', 'UI Designer', '2023-03-10', '+1-555-1002')
) AS emp(full_name, first_name, last_name, email, dept_name, position, hire_date, phone)
JOIN dept_ids ON dept_ids.name = emp.dept_name;

-- Update manager relationships
WITH employee_data AS (
  SELECT e.id, e.name, e.position, d.name as dept_name
  FROM employees e
  JOIN departments d ON e.department_id = d.id
)
UPDATE employees 
SET manager_id = (
  CASE 
    WHEN position = 'Engineering Manager' THEN NULL
    WHEN department_id = (SELECT id FROM departments WHERE name = 'Engineering') 
      THEN (SELECT id FROM employee_data WHERE position = 'Engineering Manager')
    WHEN position = 'Marketing Manager' THEN NULL
    WHEN department_id = (SELECT id FROM departments WHERE name = 'Marketing') 
      THEN (SELECT id FROM employee_data WHERE position = 'Marketing Manager')
    WHEN position = 'Sales Director' THEN NULL
    WHEN department_id = (SELECT id FROM departments WHERE name = 'Sales') 
      THEN (SELECT id FROM employee_data WHERE position = 'Sales Director')
    WHEN position = 'HR Director' THEN NULL
    WHEN department_id = (SELECT id FROM departments WHERE name = 'Human Resources') 
      THEN (SELECT id FROM employee_data WHERE position = 'HR Director')
    WHEN position = 'Finance Director' THEN NULL
    WHEN department_id = (SELECT id FROM departments WHERE name = 'Finance') 
      THEN (SELECT id FROM employee_data WHERE position = 'Finance Director')
    ELSE NULL
  END
);

-- =====================================================
-- 3. USERS (Authentication)
-- =====================================================
-- NOTE: Users are created with default passwords based on their email prefix + "123!"
-- Example: john.smith@company.com → password: John123!

INSERT INTO users (id, email, hashed_password, role, employee_id, is_active)
SELECT 
  gen_random_uuid(),
  e.email,
  -- Generate default password hash (will be overridden by admin setup script)
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBdXzogKLzPjIW', -- Default: 'password123'
  CASE 
    WHEN e.position LIKE '%Director%' OR e.position LIKE '%Manager%' THEN 'manager'
    WHEN e.department_id = (SELECT id FROM departments WHERE name = 'Human Resources') THEN 'hr_admin'
    ELSE 'employee'
  END,
  e.id,
  true
FROM employees e;

-- Set one admin user
UPDATE users SET role = 'admin' WHERE email = 'rachel.white@company.com';

-- Create super admin user (password will be set by admin setup script)
INSERT INTO users (id, email, hashed_password, role, is_active, profile_settings) VALUES
(gen_random_uuid(), 'superadmin@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBdXzogKLzPjIW', 'admin', true, '{"is_super_admin": true}'),
(gen_random_uuid(), 'demo@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBdXzogKLzPjIW', 'admin', true, '{"is_demo_admin": true}'),
(gen_random_uuid(), 'hradmin@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBdXzogKLzPjIW', 'hr_admin', true, '{"is_hr_admin": true}');

-- Note: Run the admin setup script (create_admin.py) after database population to set proper passwords

-- =====================================================
-- 4. KPI CATEGORIES
-- =====================================================
INSERT INTO kpi_categories (name, description, icon, color) VALUES
('Employee Engagement', 'Metrics related to employee satisfaction and engagement', '📊', '#3B82F6'),
('Retention', 'Employee turnover and retention metrics', '🔄', '#10B981'),
('Performance', 'Individual and team performance indicators', '🎯', '#F59E0B'),
('Training & Development', 'Learning and development metrics', '📚', '#8B5CF6'),
('Diversity & Inclusion', 'Workplace diversity and inclusion metrics', '🤝', '#EF4444'),
('Well-being', 'Employee health and wellness indicators', '💚', '#06B6D4'),
('Productivity', 'Work output and efficiency metrics', '⚡', '#F97316'),
('Communication', 'Internal communication effectiveness', '💬', '#84CC16');

-- =====================================================
-- 5. KPIS
-- =====================================================
WITH kpi_cat_ids AS (
  SELECT id, name FROM kpi_categories
)
INSERT INTO kpis (name, description, category_id, target_value, current_value, unit, measurement_frequency, calculation_method, is_active)
SELECT 
  kpi.name,
  kpi.description,
  kpi_cat_ids.id,
  kpi.target_value,
  kpi.current_value,
  kpi.unit,
  kpi.frequency,
  kpi.method,
  true
FROM (VALUES
  ('Employee Engagement Score', 'Overall engagement score from surveys', 'Employee Engagement', 80, 75, '%', 'monthly', 'survey_based'),
  ('Employee Net Promoter Score (eNPS)', 'Likelihood of employees recommending the company', 'Employee Engagement', 50, 42, 'score', 'quarterly', 'survey_based'),
  ('Turnover Rate', 'Percentage of employees who left the company', 'Retention', 10, 8, '%', 'monthly', 'automatic'),
  ('Voluntary Turnover Rate', 'Percentage of employees who voluntarily left', 'Retention', 7, 6, '%', 'monthly', 'automatic'),
  ('Time to Fill Positions', 'Average days to fill open positions', 'Performance', 30, 35, 'days', 'monthly', 'automatic'),
  ('Training Completion Rate', 'Percentage of required training completed', 'Training & Development', 95, 88, '%', 'monthly', 'automatic'),
  ('Training Effectiveness Score', 'Effectiveness of training programs', 'Training & Development', 85, 80, 'score', 'quarterly', 'survey_based'),
  ('Diversity Ratio', 'Ratio of diverse employees in the organization', 'Diversity & Inclusion', 40, 38, '%', 'quarterly', 'automatic'),
  ('Stress Level Index', 'Average stress level reported by employees', 'Well-being', 3, 3.2, 'score', 'monthly', 'survey_based'),
  ('Work-Life Balance Score', 'Employee satisfaction with work-life balance', 'Well-being', 80, 76, 'score', 'quarterly', 'survey_based'),
  ('Productivity Index', 'Overall productivity measurement', 'Productivity', 85, 82, 'score', 'monthly', 'automatic'),
  ('Absenteeism Rate', 'Percentage of unplanned absences', 'Performance', 3, 2.5, '%', 'monthly', 'automatic'),
  ('Internal Communication Effectiveness', 'Effectiveness of internal communications', 'Communication', 85, 78, 'score', 'quarterly', 'survey_based')
) AS kpi(name, description, category, target_value, current_value, unit, frequency, method)
JOIN kpi_cat_ids ON kpi_cat_ids.name = kpi.category;

-- =====================================================
-- 6. KPI VALUES (Historical Data)
-- =====================================================
WITH kpi_data AS (
  SELECT id, name, current_value FROM kpis
)
INSERT INTO kpi_values (kpi_id, value, period_start, period_end, department_id)
SELECT 
  kpi_data.id,
  kpi_data.current_value + (RANDOM() * 10 - 5), -- Add some variance
  date_trunc('month', NOW()) - INTERVAL '1 month',
  date_trunc('month', NOW()) - INTERVAL '1 day',
  (SELECT id FROM departments ORDER BY RANDOM() LIMIT 1)
FROM kpi_data, generate_series(1, 3) -- Generate 3 months of data
WHERE kpi_data.name IN ('Employee Engagement Score', 'Turnover Rate', 'Productivity Index');

-- =====================================================
-- 7. SURVEY TEMPLATES
-- =====================================================
INSERT INTO survey_templates (name, description, category, questions, is_predefined)
VALUES
('Employee Engagement Pulse', 'Quick 5-question engagement survey', 'pulse', 
 '[
   {"id": 1, "text": "How satisfied are you with your current role?", "type": "scale", "scale": 5}, 
   {"id": 2, "text": "How likely are you to recommend this company as a place to work?", "type": "scale", "scale": 10},
   {"id": 3, "text": "Do you feel your work has meaning and purpose?", "type": "scale", "scale": 5},
   {"id": 4, "text": "How well does your manager support your professional development?", "type": "scale", "scale": 5},
   {"id": 5, "text": "What one thing would improve your work experience?", "type": "text"}
 ]', true),
('Stress & Well-being Check', 'Survey to assess employee stress levels', 'pulse',
 '[
   {"id": 1, "text": "How would you rate your current stress level at work?", "type": "scale", "scale": 5},
   {"id": 2, "text": "How manageable is your current workload?", "type": "scale", "scale": 5},
   {"id": 3, "text": "How satisfied are you with your work-life balance?", "type": "scale", "scale": 5},
   {"id": 4, "text": "Do you feel you have adequate support from your team?", "type": "boolean"},
   {"id": 5, "text": "What support would help reduce your stress?", "type": "text"}
 ]', true),
('Manager Effectiveness Survey', 'Evaluate management effectiveness', 'performance',
 '[
   {"id": 1, "text": "My manager provides clear direction and expectations", "type": "scale", "scale": 5},
   {"id": 2, "text": "My manager gives me useful feedback on my performance", "type": "scale", "scale": 5},
   {"id": 3, "text": "My manager supports my career development", "type": "scale", "scale": 5},
   {"id": 4, "text": "I feel comfortable approaching my manager with concerns", "type": "scale", "scale": 5},
   {"id": 5, "text": "What could your manager do differently to better support you?", "type": "text"}
 ]', true);

-- =====================================================
-- 8. SURVEYS
-- =====================================================
INSERT INTO surveys (title, description, type, status, start_date, end_date, is_anonymous, target_departments)
VALUES
('Q1 2024 Engagement Survey', 'Quarterly employee engagement assessment', 'engagement', 'completed', '2024-01-15', '2024-01-31', true, '[]'),
('Monthly Pulse Check - March', 'Quick monthly pulse survey', 'pulse', 'completed', '2024-03-01', '2024-03-15', true, '[]'),
('Stress Assessment Survey', 'Workplace stress evaluation', 'wellbeing', 'active', '2024-03-20', '2024-04-05', true, '[]'),
('Manager Feedback Survey', 'Annual manager effectiveness survey', 'performance', 'draft', '2024-04-01', '2024-04-30', false, '[]');

-- =====================================================
-- 9. SURVEY QUESTIONS
-- =====================================================
WITH survey_data AS (
  SELECT id, title FROM surveys WHERE title = 'Q1 2024 Engagement Survey'
)
INSERT INTO survey_questions (survey_id, text, type, options)
SELECT 
  survey_data.id,
  q.text,
  q.type,
  q.options::jsonb
FROM survey_data,
(VALUES
  ('How satisfied are you with your current role?', 'scale', '{"scale": 5}'),
  ('How likely are you to recommend this company as a place to work?', 'scale', '{"scale": 10}'),
  ('Do you feel your work has meaning and purpose?', 'scale', '{"scale": 5}'),
  ('How well does your manager support your professional development?', 'scale', '{"scale": 5}'),
  ('What one thing would improve your work experience?', 'text', '{}')
) AS q(text, type, options);

-- =====================================================
-- 10. SURVEY RESPONSES
-- =====================================================
WITH survey_employee_pairs AS (
  SELECT 
    s.id as survey_id,
    e.id as employee_id,
    s.title
  FROM surveys s
  CROSS JOIN employees e
  WHERE s.status = 'completed'
  AND RANDOM() > 0.3 -- 70% response rate
)
INSERT INTO survey_responses (survey_id, employee_id, responses, completion_time_seconds, is_anonymous, submitted_at)
SELECT 
  survey_id,
  employee_id,
  jsonb_build_object(
    '1', (RANDOM() * 4 + 1)::int,
    '2', (RANDOM() * 8 + 2)::int,
    '3', (RANDOM() * 4 + 1)::int,
    '4', (RANDOM() * 4 + 1)::int,
    '5', CASE WHEN RANDOM() > 0.7 THEN 'Better work-life balance' ELSE 'More growth opportunities' END
  ),
  (RANDOM() * 300 + 60)::int, -- 1-5 minutes
  true,
  NOW() - INTERVAL '1 month' + (RANDOM() * INTERVAL '15 days')
FROM survey_employee_pairs;

-- =====================================================
-- 11. PERFORMANCE REVIEW CYCLES
-- =====================================================
INSERT INTO performance_review_cycles (name, description, type, start_date, end_date, status)
VALUES
('Annual Review 2023', 'Annual performance review cycle', 'annual', '2023-11-01', '2023-12-31', 'completed'),
('Q1 2024 Check-in', 'Quarterly performance check-in', 'quarterly', '2024-01-01', '2024-01-31', 'completed'),
('Annual Review 2024', 'Annual performance review cycle', 'annual', '2024-11-01', '2024-12-31', 'active');

-- =====================================================
-- 12. PERFORMANCE REVIEWS
-- =====================================================
WITH review_cycle AS (
  SELECT id FROM performance_review_cycles WHERE name = 'Q1 2024 Check-in'
),
employee_manager_pairs AS (
  SELECT 
    e.id as employee_id,
    e.manager_id as reviewer_id,
    e.name as employee_name,
    m.name as manager_name
  FROM employees e
  LEFT JOIN employees m ON e.manager_id = m.id
  WHERE e.manager_id IS NOT NULL
)
INSERT INTO performance_reviews (cycle_id, employee_id, reviewer_id, rating, comments, status, self_assessment, manager_feedback)
SELECT 
  (SELECT id FROM review_cycle),
  emp.employee_id,
  emp.reviewer_id,
  (RANDOM() * 2 + 3)::int, -- Rating between 3-5
  CASE 
    WHEN RANDOM() > 0.7 THEN 'Excellent performance and strong collaboration skills'
    WHEN RANDOM() > 0.4 THEN 'Good work quality with room for improvement in communication'
    ELSE 'Meets expectations with potential for growth'
  END,
  'completed',
  jsonb_build_object(
    'achievements', 'Successfully completed major project deliverables',
    'challenges', 'Time management during peak periods',
    'goals', 'Improve technical skills and take on leadership role'
  ),
  jsonb_build_object(
    'strengths', 'Strong technical abilities and teamwork',
    'areas_for_improvement', 'Communication and project planning',
    'support_needed', 'Additional training in leadership skills'
  )
FROM employee_manager_pairs emp
WHERE RANDOM() > 0.2; -- 80% completion rate

-- =====================================================
-- 13. PERFORMANCE GOALS
-- =====================================================
WITH recent_reviews AS (
  SELECT id, employee_id FROM performance_reviews WHERE status = 'completed'
)
INSERT INTO performance_goals (review_id, description, status, due_date)
SELECT 
  rr.id,
  goal.description,
  goal.status,
  (NOW() + INTERVAL '3 months')::date
FROM recent_reviews rr,
(VALUES
  ('Complete advanced technical certification', 'pending'),
  ('Improve code review turnaround time by 50%', 'in_progress'),
  ('Mentor junior team member', 'pending'),
  ('Lead cross-functional project', 'pending'),
  ('Enhance presentation skills through training', 'in_progress')
) AS goal(description, status)
WHERE RANDOM() > 0.4; -- Each review gets 2-3 goals on average

-- =====================================================
-- 14. FOCUS GROUPS
-- =====================================================
WITH user_data AS (
  SELECT u.id as user_id, e.id as employee_id, e.department_id, d.name as dept_name
  FROM users u
  JOIN employees e ON u.employee_id = e.id
  JOIN departments d ON e.department_id = d.id
)
INSERT INTO focus_groups (name, description, type, criteria, members, status, created_by)
SELECT 
  fg.name,
  fg.description,
  fg.type,
  fg.criteria::jsonb,
  fg.members::jsonb,
  'active',
  (SELECT user_id FROM user_data WHERE dept_name = 'Human Resources' LIMIT 1)
FROM (VALUES
  ('High Performers', 'Top performing employees across departments', 'performance', 
   '{"performance_rating": ">=4", "tenure": ">=1_year"}',
   (SELECT jsonb_agg(e.id) FROM employees e JOIN performance_reviews pr ON e.id = pr.employee_id WHERE pr.rating >= 4 LIMIT 8)::text),
  ('New Hires Cohort', 'Recently hired employees for onboarding focus', 'custom',
   '{"hire_date": ">=2023-01-01"}',
   (SELECT jsonb_agg(e.id) FROM employees e WHERE e.hire_date >= '2023-01-01' LIMIT 10)::text),
  ('Engineering Team Leads', 'Senior engineering professionals', 'department',
   '{"department": "Engineering", "seniority": "Senior"}',
   (SELECT jsonb_agg(e.id) FROM employees e JOIN departments d ON e.department_id = d.id WHERE d.name = 'Engineering' AND e.position LIKE '%Senior%' LIMIT 5)::text),
  ('Remote Work Advocates', 'Employees advocating for flexible work arrangements', 'survey_based',
   '{"survey_response": "work_from_home_preference"}',
   (SELECT jsonb_agg(e.id) FROM employees e LIMIT 6)::text)
) AS fg(name, description, type, criteria, members);

-- =====================================================
-- 15. ACTION PLAN TEMPLATES
-- =====================================================
INSERT INTO action_plan_templates (title, description, category, steps, estimated_duration_days, is_ai_generated, effectiveness_score)
VALUES
('Team Building Workshop', 'Improve team cohesion and collaboration', 'engagement',
 '[
   {"step": 1, "title": "Plan workshop activities", "duration": 3, "responsible": "HR"},
   {"step": 2, "title": "Book venue and facilitator", "duration": 5, "responsible": "HR"},
   {"step": 3, "title": "Conduct team building workshop", "duration": 1, "responsible": "Manager"},
   {"step": 4, "title": "Follow-up survey", "duration": 7, "responsible": "HR"}
 ]', 30, false, 8.2),
('Stress Reduction Program', 'Implement stress management initiatives', 'wellbeing',
 '[
   {"step": 1, "title": "Assess current stress levels", "duration": 7, "responsible": "HR"},
   {"step": 2, "title": "Design stress reduction activities", "duration": 14, "responsible": "HR"},
   {"step": 3, "title": "Launch mindfulness program", "duration": 30, "responsible": "Wellness Team"},
   {"step": 4, "title": "Monitor progress and adjust", "duration": 60, "responsible": "HR"}
 ]', 90, true, 7.8),
('Manager Training Program', 'Enhance management effectiveness', 'performance',
 '[
   {"step": 1, "title": "Identify training needs", "duration": 5, "responsible": "HR"},
   {"step": 2, "title": "Develop training curriculum", "duration": 21, "responsible": "Training Team"},
   {"step": 3, "title": "Deliver management training", "duration": 30, "responsible": "External Trainer"},
   {"step": 4, "title": "Assess training effectiveness", "duration": 14, "responsible": "HR"}
 ]', 60, false, 8.5);

-- =====================================================
-- 16. ACTION PLANS
-- =====================================================
WITH template_ids AS (
  SELECT id, title FROM action_plan_templates
),
focus_group_ids AS (
  SELECT id, name FROM focus_groups
),
hr_user AS (
  SELECT u.id FROM users u JOIN employees e ON u.employee_id = e.id JOIN departments d ON e.department_id = d.id WHERE d.name = 'Human Resources' LIMIT 1
)
INSERT INTO action_plans (template_id, title, description, target_focus_group_id, status, priority, start_date, end_date, assigned_to, progress_percentage, created_by)
SELECT 
  t.id,
  'Q2 ' || t.title,
  'Implementation of ' || t.title || ' for targeted employee groups',
  fg.id,
  CASE WHEN RANDOM() > 0.5 THEN 'in_progress' ELSE 'planned' END,
  CASE WHEN RANDOM() > 0.7 THEN 'high' WHEN RANDOM() > 0.4 THEN 'medium' ELSE 'low' END,
  NOW()::date,
  (NOW() + INTERVAL '2 months')::date,
  hr.id,
  (RANDOM() * 60)::int,
  hr.id
FROM template_ids t
CROSS JOIN focus_group_ids fg
CROSS JOIN hr_user hr
WHERE RANDOM() > 0.5 -- Create some action plans
LIMIT 6;

-- =====================================================
-- 17. ONE-ON-ONE MEETINGS
-- =====================================================
WITH manager_employee_pairs AS (
  SELECT 
    e.id as employee_id,
    e.manager_id,
    e.name as employee_name
  FROM employees e
  WHERE e.manager_id IS NOT NULL
)
INSERT INTO one_on_one_meetings (employee_id, manager_id, scheduled_date, actual_date, duration_minutes, agenda, notes, status, meeting_type)
SELECT 
  mep.employee_id,
  mep.manager_id,
  NOW() - INTERVAL '2 weeks' + (RANDOM() * INTERVAL '4 weeks'),
  CASE WHEN RANDOM() > 0.2 THEN NOW() - INTERVAL '2 weeks' + (RANDOM() * INTERVAL '4 weeks') ELSE NULL END,
  CASE WHEN RANDOM() > 0.2 THEN (RANDOM() * 30 + 30)::int ELSE NULL END,
  '["Career development discussion", "Current project status", "Feedback and concerns", "Goal setting"]'::jsonb,
  CASE 
    WHEN RANDOM() > 0.3 THEN 'Good discussion about career growth opportunities. Employee interested in taking on more responsibilities.'
    ELSE NULL
  END,
  CASE WHEN RANDOM() > 0.2 THEN 'completed' ELSE 'scheduled' END,
  'regular'
FROM manager_employee_pairs mep
WHERE RANDOM() > 0.3; -- 70% of employees have recent 1:1s

-- =====================================================
-- 18. FEEDBACK
-- =====================================================
INSERT INTO feedback (recipient_id, giver_id, feedback_type, category, content, rating, is_anonymous)
SELECT 
  e1.id,
  e2.id,
  CASE 
    WHEN e1.manager_id = e2.id THEN 'downward'
    WHEN e2.manager_id = e1.id THEN 'upward'
    ELSE 'peer'
  END,
  (ARRAY['performance', 'behavior', 'skills', 'communication'])[floor(random() * 4 + 1)],
  CASE 
    WHEN RANDOM() > 0.7 THEN 'Excellent collaboration and always delivers high-quality work'
    WHEN RANDOM() > 0.4 THEN 'Good team player with strong technical skills'
    ELSE 'Reliable and consistent performer with great attitude'
  END,
  (RANDOM() * 2 + 3)::int,
  RANDOM() > 0.5
FROM employees e1
CROSS JOIN employees e2
WHERE e1.id != e2.id
AND e1.department_id = e2.department_id
AND RANDOM() > 0.8 -- Limited feedback entries
LIMIT 25;

-- =====================================================
-- 19. PRAISE AND RECOGNITION
-- =====================================================
INSERT INTO praise_recognition (recipient_id, giver_id, type, title, description, category, visibility)
SELECT 
  e1.id,
  e2.id,
  (ARRAY['praise', 'recognition', 'achievement'])[floor(random() * 3 + 1)],
  CASE 
    WHEN RANDOM() > 0.7 THEN 'Outstanding Project Delivery'
    WHEN RANDOM() > 0.4 THEN 'Excellent Team Collaboration'
    ELSE 'Innovation and Problem Solving'
  END,
  CASE 
    WHEN RANDOM() > 0.7 THEN 'Delivered the project ahead of schedule with exceptional quality'
    WHEN RANDOM() > 0.4 THEN 'Showed great leadership in helping team members and sharing knowledge'
    ELSE 'Came up with creative solution that saved significant time and resources'
  END,
  (ARRAY['teamwork', 'innovation', 'leadership', 'achievement'])[floor(random() * 4 + 1)],
  (ARRAY['team', 'department', 'company'])[floor(random() * 3 + 1)]
FROM employees e1
CROSS JOIN employees e2
WHERE e1.id != e2.id
AND RANDOM() > 0.9 -- Limited praise entries
LIMIT 15;

-- =====================================================
-- 20. OUTLIERS (Problem Identification)
-- =====================================================
WITH low_engagement_employees AS (
  SELECT DISTINCT sr.employee_id
  FROM survey_responses sr
  WHERE (sr.responses->>'1')::int <= 2 OR (sr.responses->>'3')::int <= 2
),
high_stress_employees AS (
  SELECT e.id as employee_id
  FROM employees e
  WHERE RANDOM() > 0.9 -- Simulate 10% high stress
)
INSERT INTO outliers (employee_id, type, category, severity, metrics, contributing_factors, focus_group_id)
SELECT 
  lee.employee_id,
  'survey_based',
  'engagement',
  CASE WHEN RANDOM() > 0.7 THEN 'high' ELSE 'medium' END,
  '{"engagement_score": 2, "survey_responses": "low_satisfaction"}'::jsonb,
  '["workload", "lack_of_recognition", "limited_growth_opportunities"]'::jsonb,
  (SELECT id FROM focus_groups WHERE type = 'performance' LIMIT 1)
FROM low_engagement_employees lee
LIMIT 5;

-- =====================================================
-- FINAL CLEANUP
-- =====================================================

-- Re-enable RLS
SET session_replication_role = DEFAULT;

-- Update department managers
UPDATE departments SET manager_id = (
  SELECT e.id FROM employees e 
  WHERE e.department_id = departments.id 
  AND (e.position LIKE '%Manager%' OR e.position LIKE '%Director%')
  LIMIT 1
);

-- Create some notification queue entries
INSERT INTO notification_queue (recipient_id, type, title, message, platform, status)
SELECT 
  u.id,
  'survey_invitation',
  'New Survey Available',
  'You have been invited to participate in the monthly engagement survey',
  'email',
  'pending'
FROM users u
WHERE RANDOM() > 0.7
LIMIT 10;

-- =====================================================
-- SUMMARY STATISTICS
-- =====================================================
SELECT 
  'Data Population Complete!' as status,
  (SELECT COUNT(*) FROM departments) as departments_count,
  (SELECT COUNT(*) FROM employees) as employees_count,
  (SELECT COUNT(*) FROM users) as users_count,
  (SELECT COUNT(*) FROM kpis) as kpis_count,
  (SELECT COUNT(*) FROM surveys) as surveys_count,
  (SELECT COUNT(*) FROM survey_responses) as survey_responses_count,
  (SELECT COUNT(*) FROM performance_reviews) as performance_reviews_count,
  (SELECT COUNT(*) FROM focus_groups) as focus_groups_count,
  (SELECT COUNT(*) FROM action_plans) as action_plans_count; 