-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.action_plan_progress (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  action_plan_id uuid,
  milestone_name text NOT NULL,
  status text NOT NULL,
  progress_percentage integer DEFAULT 0,
  notes text,
  updated_by uuid,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT action_plan_progress_pkey PRIMARY KEY (id),
  CONSTRAINT action_plan_progress_action_plan_id_fkey FOREIGN KEY (action_plan_id) REFERENCES public.action_plans(id),
  CONSTRAINT action_plan_progress_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id)
);
CREATE TABLE public.action_plan_templates (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  title text NOT NULL UNIQUE,
  description text,
  category text NOT NULL,
  steps jsonb NOT NULL,
  estimated_duration_days integer,
  success_metrics jsonb DEFAULT '[]'::jsonb,
  is_ai_generated boolean DEFAULT false,
  effectiveness_score numeric,
  tags jsonb DEFAULT '[]'::jsonb,
  created_by uuid,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT action_plan_templates_pkey PRIMARY KEY (id),
  CONSTRAINT action_plan_templates_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id)
);
CREATE TABLE public.action_plans (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  template_id uuid,
  title text NOT NULL,
  description text,
  target_focus_group_id uuid,
  target_departments jsonb DEFAULT '[]'::jsonb,
  target_employees jsonb DEFAULT '[]'::jsonb,
  target_kpis jsonb DEFAULT '[]'::jsonb,
  status text DEFAULT 'planned'::text,
  priority text DEFAULT 'medium'::text,
  start_date date,
  end_date date,
  actual_start_date date,
  actual_end_date date,
  assigned_to uuid,
  stakeholders jsonb DEFAULT '[]'::jsonb,
  milestones jsonb DEFAULT '[]'::jsonb,
  progress_percentage integer DEFAULT 0,
  budget numeric,
  resources_required jsonb DEFAULT '[]'::jsonb,
  created_by uuid,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT action_plans_pkey PRIMARY KEY (id),
  CONSTRAINT action_plans_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.action_plan_templates(id),
  CONSTRAINT action_plans_target_focus_group_id_fkey FOREIGN KEY (target_focus_group_id) REFERENCES public.focus_groups(id),
  CONSTRAINT action_plans_assigned_to_fkey FOREIGN KEY (assigned_to) REFERENCES public.users(id),
  CONSTRAINT action_plans_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id)
);
CREATE TABLE public.advanced_kpis (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  kpi_code text NOT NULL UNIQUE,
  name text NOT NULL,
  description text,
  formula_expression text NOT NULL,
  parameter_weights jsonb NOT NULL,
  calculation_frequency text DEFAULT 'quarterly'::text,
  target_value numeric,
  unit text DEFAULT 'score'::text,
  is_active boolean DEFAULT true,
  created_by uuid,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  CONSTRAINT advanced_kpis_pkey PRIMARY KEY (id),
  CONSTRAINT advanced_kpis_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id)
);
CREATE TABLE public.analytics_events (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid,
  event_type text NOT NULL,
  event_data jsonb NOT NULL,
  session_id text,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT analytics_events_pkey PRIMARY KEY (id),
  CONSTRAINT analytics_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.audit_logs (
  id uuid NOT NULL,
  user_id uuid,
  action character varying NOT NULL,
  details json,
  ip_address character varying,
  user_agent character varying,
  timestamp timestamp with time zone DEFAULT now(),
  CONSTRAINT audit_logs_pkey PRIMARY KEY (id),
  CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.consent_records (
  id uuid NOT NULL,
  user_id uuid,
  consent_type character varying NOT NULL,
  purpose character varying NOT NULL,
  data_categories json,
  consent_given boolean NOT NULL,
  consent_text text,
  ip_address character varying,
  user_agent character varying,
  created_at timestamp with time zone DEFAULT now(),
  expires_at timestamp with time zone,
  CONSTRAINT consent_records_pkey PRIMARY KEY (id),
  CONSTRAINT consent_records_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.dashboard_configs (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid,
  name text NOT NULL,
  layout jsonb NOT NULL,
  widgets jsonb NOT NULL,
  is_default boolean DEFAULT false,
  is_shared boolean DEFAULT false,
  shared_with jsonb DEFAULT '[]'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT dashboard_configs_pkey PRIMARY KEY (id),
  CONSTRAINT dashboard_configs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.data_retention_policies (
  id uuid NOT NULL,
  name character varying NOT NULL,
  description text,
  data_type character varying NOT NULL,
  retention_period_days integer NOT NULL,
  auto_delete boolean,
  legal_basis character varying,
  is_active boolean,
  created_by uuid,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT data_retention_policies_pkey PRIMARY KEY (id),
  CONSTRAINT data_retention_policies_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id)
);
CREATE TABLE public.departments (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name text NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  description text,
  manager_id uuid,
  CONSTRAINT departments_pkey PRIMARY KEY (id),
  CONSTRAINT departments_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.employees(id)
);
CREATE TABLE public.efficacy_measurements (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  action_plan_id uuid,
  measurement_type text NOT NULL,
  kpi_id uuid,
  baseline_value numeric,
  measured_value numeric,
  improvement_percentage numeric,
  improvement_absolute numeric,
  statistical_significance numeric,
  measurement_date timestamp with time zone NOT NULL,
  survey_id uuid,
  notes text,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT efficacy_measurements_pkey PRIMARY KEY (id),
  CONSTRAINT efficacy_measurements_action_plan_id_fkey FOREIGN KEY (action_plan_id) REFERENCES public.action_plans(id),
  CONSTRAINT efficacy_measurements_kpi_id_fkey FOREIGN KEY (kpi_id) REFERENCES public.kpis(id),
  CONSTRAINT efficacy_measurements_survey_id_fkey FOREIGN KEY (survey_id) REFERENCES public.surveys(id)
);
CREATE TABLE public.employee_advanced_kpi_values (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  employee_id uuid NOT NULL,
  kpi_code text NOT NULL,
  calculated_value numeric NOT NULL,
  component_scores jsonb NOT NULL,
  calculation_date timestamp with time zone DEFAULT now(),
  period_start date NOT NULL,
  period_end date NOT NULL,
  confidence_score numeric DEFAULT 1.0,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  CONSTRAINT employee_advanced_kpi_values_pkey PRIMARY KEY (employee_id, kpi_code, period_start),
  CONSTRAINT employee_advanced_kpi_values_kpi_code_fkey FOREIGN KEY (kpi_code) REFERENCES public.advanced_kpis(kpi_code),
  CONSTRAINT employee_advanced_kpi_values_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id)
);
CREATE TABLE public.employee_ai_insights (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  employee_id uuid NOT NULL,
  insight_type text NOT NULL,
  insight_data jsonb NOT NULL,
  confidence_score numeric,
  model_version text,
  generated_at timestamp with time zone DEFAULT now(),
  expires_at timestamp with time zone,
  is_actionable boolean DEFAULT false,
  CONSTRAINT employee_ai_insights_pkey PRIMARY KEY (id),
  CONSTRAINT employee_ai_insights_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id)
);
CREATE TABLE public.employee_parameter_ratings (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  employee_id uuid NOT NULL,
  parameter_id text NOT NULL,
  rating_value numeric NOT NULL CHECK (rating_value >= 1.0 AND rating_value <= 5.0),
  rater_id uuid,
  rater_type text NOT NULL CHECK (rater_type = ANY (ARRAY['self'::text, 'manager'::text, 'peer'::text, 'system'::text])),
  evidence_text text,
  confidence_score numeric DEFAULT 1.0 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
  rating_period_start date NOT NULL,
  rating_period_end date NOT NULL,
  review_cycle_id uuid,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  CONSTRAINT employee_parameter_ratings_pkey PRIMARY KEY (id),
  CONSTRAINT employee_parameter_ratings_rater_id_fkey FOREIGN KEY (rater_id) REFERENCES public.employees(id),
  CONSTRAINT employee_parameter_ratings_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id),
  CONSTRAINT employee_parameter_ratings_parameter_id_fkey FOREIGN KEY (parameter_id) REFERENCES public.evaluation_parameters(parameter_id),
  CONSTRAINT employee_parameter_ratings_review_cycle_id_fkey FOREIGN KEY (review_cycle_id) REFERENCES public.performance_review_cycles(id)
);
CREATE TABLE public.employees (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name text NOT NULL,
  email text NOT NULL UNIQUE,
  department_id uuid,
  position text NOT NULL,
  hire_date date NOT NULL,
  status text NOT NULL DEFAULT 'active'::text,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  first_name text,
  last_name text,
  phone text,
  manager_id uuid,
  is_active boolean DEFAULT true,
  profile_data jsonb DEFAULT '{}'::jsonb,
  skills jsonb DEFAULT '[]'::jsonb,
  competencies jsonb DEFAULT '{}'::jsonb,
  CONSTRAINT employees_pkey PRIMARY KEY (id),
  CONSTRAINT employees_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id),
  CONSTRAINT employees_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.employees(id)
);
CREATE TABLE public.evaluation_parameters (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  parameter_id text NOT NULL UNIQUE,
  name text NOT NULL,
  category text NOT NULL,
  definition text NOT NULL,
  relevance_summary text,
  behavioral_anchors jsonb NOT NULL,
  is_active boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  CONSTRAINT evaluation_parameters_pkey PRIMARY KEY (id)
);
CREATE TABLE public.feedback (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  recipient_id uuid,
  giver_id uuid,
  feedback_type text NOT NULL,
  category text,
  content text NOT NULL,
  rating integer CHECK (rating >= 1 AND rating <= 5),
  is_anonymous boolean DEFAULT false,
  related_review_id uuid,
  tags jsonb DEFAULT '[]'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT feedback_pkey PRIMARY KEY (id),
  CONSTRAINT feedback_recipient_id_fkey FOREIGN KEY (recipient_id) REFERENCES public.employees(id),
  CONSTRAINT feedback_giver_id_fkey FOREIGN KEY (giver_id) REFERENCES public.employees(id),
  CONSTRAINT feedback_related_review_id_fkey FOREIGN KEY (related_review_id) REFERENCES public.performance_reviews(id)
);
CREATE TABLE public.feedback_requests (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  employee_id uuid NOT NULL,
  requested_by uuid NOT NULL,
  request_type text NOT NULL CHECK (request_type = ANY (ARRAY['360'::text, 'peer'::text, 'upward'::text, 'self'::text])),
  parameters_to_rate ARRAY NOT NULL,
  target_raters ARRAY NOT NULL,
  due_date date NOT NULL,
  status text DEFAULT 'pending'::text CHECK (status = ANY (ARRAY['pending'::text, 'in_progress'::text, 'completed'::text, 'expired'::text])),
  instructions text,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  completed_at timestamp with time zone,
  CONSTRAINT feedback_requests_pkey PRIMARY KEY (id),
  CONSTRAINT feedback_requests_requested_by_fkey FOREIGN KEY (requested_by) REFERENCES public.users(id),
  CONSTRAINT feedback_requests_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id)
);
CREATE TABLE public.focus_groups (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name text NOT NULL,
  description text,
  type text NOT NULL,
  criteria jsonb NOT NULL,
  members jsonb NOT NULL,
  status text DEFAULT 'active'::text,
  created_by uuid,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT focus_groups_pkey PRIMARY KEY (id),
  CONSTRAINT focus_groups_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id)
);
CREATE TABLE public.integration_configs (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  platform text NOT NULL,
  config_data jsonb NOT NULL,
  is_active boolean DEFAULT true,
  department_id uuid,
  created_by uuid,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT integration_configs_pkey PRIMARY KEY (id),
  CONSTRAINT integration_configs_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id),
  CONSTRAINT integration_configs_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id)
);
CREATE TABLE public.kpi_categories (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  description text,
  icon text,
  color text,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT kpi_categories_pkey PRIMARY KEY (id)
);
CREATE TABLE public.kpi_values (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  kpi_id uuid,
  value numeric NOT NULL,
  period_start timestamp with time zone NOT NULL,
  period_end timestamp with time zone NOT NULL,
  department_id uuid,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT kpi_values_pkey PRIMARY KEY (id),
  CONSTRAINT kpi_values_kpi_id_fkey FOREIGN KEY (kpi_id) REFERENCES public.kpis(id),
  CONSTRAINT kpi_values_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id)
);
CREATE TABLE public.kpis (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  description text,
  category_id uuid,
  target_value numeric,
  current_value numeric DEFAULT 0,
  unit text,
  measurement_frequency text NOT NULL,
  calculation_method text,
  is_custom boolean DEFAULT false,
  is_active boolean DEFAULT true,
  target_departments jsonb DEFAULT '[]'::jsonb,
  target_employee_groups jsonb DEFAULT '[]'::jsonb,
  alert_threshold_low numeric,
  alert_threshold_high numeric,
  created_by uuid,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT kpis_pkey PRIMARY KEY (id),
  CONSTRAINT kpis_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.kpi_categories(id),
  CONSTRAINT kpis_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id)
);
CREATE TABLE public.notification_queue (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  recipient_id uuid,
  type text NOT NULL,
  title text NOT NULL,
  message text NOT NULL,
  platform text NOT NULL,
  status text DEFAULT 'pending'::text,
  scheduled_for timestamp with time zone DEFAULT now(),
  sent_at timestamp with time zone,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT notification_queue_pkey PRIMARY KEY (id),
  CONSTRAINT notification_queue_recipient_id_fkey FOREIGN KEY (recipient_id) REFERENCES public.users(id)
);
CREATE TABLE public.one_on_one_meetings (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  employee_id uuid,
  manager_id uuid,
  scheduled_date timestamp with time zone NOT NULL,
  actual_date timestamp with time zone,
  duration_minutes integer,
  agenda jsonb DEFAULT '[]'::jsonb,
  notes text,
  action_items jsonb DEFAULT '[]'::jsonb,
  status text DEFAULT 'scheduled'::text,
  meeting_type text DEFAULT 'regular'::text,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT one_on_one_meetings_pkey PRIMARY KEY (id),
  CONSTRAINT one_on_one_meetings_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id),
  CONSTRAINT one_on_one_meetings_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.employees(id)
);
CREATE TABLE public.outliers (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  employee_id uuid,
  type text NOT NULL,
  category text NOT NULL,
  severity text NOT NULL,
  metrics jsonb NOT NULL,
  contributing_factors jsonb DEFAULT '[]'::jsonb,
  is_resolved boolean DEFAULT false,
  focus_group_id uuid,
  identified_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  resolved_at timestamp with time zone,
  CONSTRAINT outliers_pkey PRIMARY KEY (id),
  CONSTRAINT outliers_focus_group_id_fkey FOREIGN KEY (focus_group_id) REFERENCES public.focus_groups(id),
  CONSTRAINT outliers_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id)
);
CREATE TABLE public.parameter_rating_history (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  employee_parameter_rating_id uuid NOT NULL,
  old_rating_value numeric,
  new_rating_value numeric,
  change_reason text,
  changed_by uuid,
  changed_at timestamp with time zone DEFAULT now(),
  CONSTRAINT parameter_rating_history_pkey PRIMARY KEY (id),
  CONSTRAINT parameter_rating_history_employee_parameter_rating_id_fkey FOREIGN KEY (employee_parameter_rating_id) REFERENCES public.employee_parameter_ratings(id),
  CONSTRAINT parameter_rating_history_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES public.users(id)
);
CREATE TABLE public.performance_goals (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  review_id uuid,
  description text NOT NULL,
  status text NOT NULL DEFAULT 'pending'::text,
  due_date date NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT performance_goals_pkey PRIMARY KEY (id),
  CONSTRAINT performance_goals_review_id_fkey FOREIGN KEY (review_id) REFERENCES public.performance_reviews(id)
);
CREATE TABLE public.performance_review_cycles (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name text NOT NULL,
  description text,
  type text NOT NULL,
  start_date date NOT NULL,
  end_date date NOT NULL,
  status text DEFAULT 'planning'::text,
  departments jsonb DEFAULT '[]'::jsonb,
  template_config jsonb DEFAULT '{}'::jsonb,
  created_by uuid,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT performance_review_cycles_pkey PRIMARY KEY (id),
  CONSTRAINT performance_review_cycles_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id)
);
CREATE TABLE public.performance_reviews (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  employee_id uuid,
  reviewer_id uuid,
  rating integer NOT NULL CHECK (rating >= 1 AND rating <= 5),
  comments text,
  status text NOT NULL DEFAULT 'pending'::text,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  cycle_id uuid,
  self_assessment jsonb DEFAULT '{}'::jsonb,
  peer_feedback jsonb DEFAULT '[]'::jsonb,
  manager_feedback jsonb DEFAULT '{}'::jsonb,
  goals_for_next_period jsonb DEFAULT '[]'::jsonb,
  calibration_score numeric,
  review_type text DEFAULT 'annual'::text,
  CONSTRAINT performance_reviews_pkey PRIMARY KEY (id),
  CONSTRAINT performance_reviews_reviewer_id_fkey FOREIGN KEY (reviewer_id) REFERENCES public.employees(id),
  CONSTRAINT performance_reviews_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id),
  CONSTRAINT performance_reviews_cycle_id_fkey FOREIGN KEY (cycle_id) REFERENCES public.performance_review_cycles(id)
);
CREATE TABLE public.praise_recognition (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  recipient_id uuid,
  giver_id uuid,
  type text NOT NULL,
  title text NOT NULL,
  description text,
  category text,
  visibility text DEFAULT 'team'::text,
  platform_posted jsonb DEFAULT '[]'::jsonb,
  reactions jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT praise_recognition_pkey PRIMARY KEY (id),
  CONSTRAINT praise_recognition_recipient_id_fkey FOREIGN KEY (recipient_id) REFERENCES public.employees(id),
  CONSTRAINT praise_recognition_giver_id_fkey FOREIGN KEY (giver_id) REFERENCES public.employees(id)
);
CREATE TABLE public.survey_kpi_mappings (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  survey_id uuid,
  kpi_id uuid,
  question_mapping jsonb NOT NULL,
  weight numeric DEFAULT 1.0,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT survey_kpi_mappings_pkey PRIMARY KEY (id),
  CONSTRAINT survey_kpi_mappings_survey_id_fkey FOREIGN KEY (survey_id) REFERENCES public.surveys(id),
  CONSTRAINT survey_kpi_mappings_kpi_id_fkey FOREIGN KEY (kpi_id) REFERENCES public.kpis(id)
);
CREATE TABLE public.survey_questions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  survey_id uuid,
  text text NOT NULL,
  type text NOT NULL,
  options jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT survey_questions_pkey PRIMARY KEY (id),
  CONSTRAINT survey_questions_survey_id_fkey FOREIGN KEY (survey_id) REFERENCES public.surveys(id)
);
CREATE TABLE public.survey_responses (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  survey_id uuid,
  employee_id uuid,
  responses jsonb NOT NULL,
  completion_time_seconds integer,
  is_anonymous boolean DEFAULT false,
  submitted_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  metadata jsonb DEFAULT '{}'::jsonb,
  CONSTRAINT survey_responses_pkey PRIMARY KEY (id),
  CONSTRAINT survey_responses_survey_id_fkey FOREIGN KEY (survey_id) REFERENCES public.surveys(id),
  CONSTRAINT survey_responses_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id)
);
CREATE TABLE public.survey_templates (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  description text,
  category text,
  questions jsonb NOT NULL,
  is_predefined boolean DEFAULT false,
  tags jsonb DEFAULT '[]'::jsonb,
  created_by uuid,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT survey_templates_pkey PRIMARY KEY (id),
  CONSTRAINT survey_templates_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id)
);
CREATE TABLE public.surveys (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  title text NOT NULL,
  description text,
  type text NOT NULL,
  status text NOT NULL DEFAULT 'draft'::text,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  end_date timestamp with time zone NOT NULL,
  start_date timestamp with time zone DEFAULT now(),
  is_anonymous boolean DEFAULT false,
  target_departments jsonb DEFAULT '[]'::jsonb,
  target_employees jsonb DEFAULT '[]'::jsonb,
  frequency text DEFAULT 'one-time'::text,
  platform_integrations jsonb DEFAULT '{}'::jsonb,
  updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  CONSTRAINT surveys_pkey PRIMARY KEY (id)
);
CREATE TABLE public.users (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  email text NOT NULL UNIQUE,
  hashed_password text,
  role text NOT NULL DEFAULT 'employee'::text,
  is_active boolean DEFAULT true,
  employee_id uuid,
  last_login timestamp with time zone,
  profile_settings jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  CONSTRAINT users_pkey PRIMARY KEY (id),
  CONSTRAINT users_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id)
);