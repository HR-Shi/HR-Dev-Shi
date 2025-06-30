export interface User {
  id: string;
  email: string;
  role: 'admin' | 'hr' | 'manager' | 'employee';
  created_at: string;
}

export interface Department {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface Employee {
  id: string;
  name: string;
  email: string;
  department_id: string;
  position: string;
  hire_date: string;
  status: string;
  created_at: string;
  updated_at: string;
  departments?: Department;
}

export interface Survey {
  id: string;
  title: string;
  description: string;
  type: string;
  status: string;
  created_at: string;
  end_date: string;
}

export interface SurveyQuestion {
  id: string;
  survey_id: string;
  text: string;
  type: string;
  options: any;
  created_at: string;
}

export interface PerformanceReview {
  id: string;
  employee_id: string;
  reviewer_id: string;
  rating: number;
  comments: string;
  status: string;
  created_at: string;
  updated_at: string;
  employee?: Employee;
  reviewer?: Employee;
}

export interface PerformanceGoal {
  id: string;
  review_id: string;
  description: string;
  status: string;
  due_date: string;
  created_at: string;
  updated_at: string;
}

export interface KPI {
  id: string;
  name: string;
  target_value: number;
  current_value: number;
  measurement_frequency: string;
  department_id: string;
  last_updated: string;
  created_at: string;
  updated_at: string;
  departments?: Department;
}

export interface ActionPlan {
  id: string;
  title: string;
  description: string;
  category: string;
  ai_generated: boolean;
  status: 'active' | 'completed' | 'draft';
  target_kpi: string;
  efficacy_score?: number;
  created_at: string;
  updated_at: string;
}

export interface FocusGroup {
  id: string;
  name: string;
  description: string;
  employee_count: number;
  created_at: string;
  status: string;
}

export interface Initiative {
  id: string;
  title: string;
  description: string;
  status: string;
  progress: number;
  start_date: string;
  end_date: string;
  owner: string;
  participants: number;
  category: string;
  kpis: string[];
  created_at: string;
  updated_at: string;
}

export interface DashboardOverview {
  total_employees: number;
  high_concern: number;
  mid_concern: number;
  good_status: number;
  avg_engagement: number;
  active_surveys: number;
  active_action_plans: number;
  engagement_trend: number[];
}

export interface Outlier {
  id: string;
  name: string;
  department: string;
  engagement_score: number;
  status: string;
  risk_factors: string[];
}