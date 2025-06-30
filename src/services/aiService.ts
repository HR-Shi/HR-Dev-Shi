import axios from 'axios';

// Prefer the deployment backend URL when provided via environment variable
// Fallback to localhost for local development.
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api';

export interface AIActionPlan {
  title: string;
  description: string;
  category: string;
  steps: Array<{
    step: string;
    timeline: string;
    responsible: string;
  }>;
  success_metrics: string[];
  estimated_duration: string;
  target_kpi: string;
  expected_improvement: string;
}

export interface OutlierAnalysis {
  high_risk_employees: Array<{
    employee_id: string;
    name: string;
    risk_factors: string[];
    recommended_actions: string[];
    priority_score: number;
  }>;
  medium_risk_employees: Array<{
    employee_id: string;
    name: string;
    risk_factors: string[];
    recommended_actions: string[];
    priority_score: number;
  }>;
  insights: Array<{
    category: string;
    finding: string;
    recommendation: string;
  }>;
  department_trends: Record<string, {
    average_engagement: number;
    trend: string;
    key_issues: string[];
  }>;
}

export interface SurveyQuestion {
  question: string;
  type: 'likert' | 'multiple_choice' | 'text' | 'rating';
  options: string[] | null;
  kpi_mapping: string;
  weight: number;
}

export interface EfficacyAnalysis {
  efficacy_score: number;
  improvement_percentage: number;
  success_factors: string[];
  areas_for_improvement: string[];
  recommendations: Array<{
    category: string;
    recommendation: string;
    priority: string;
  }>;
  kpi_impacts: Record<string, {
    before: number;
    after: number;
    change: string;
  }>;
  overall_assessment: string;
}

export interface PerformanceInsights {
  performance_summary: {
    overall_rating: string;
    trend: string;
    key_strengths: string[];
    development_areas: string[];
  };
  recommendations: Array<{
    category: string;
    action: string;
    timeline: string;
    expected_outcome: string;
  }>;
  career_development: {
    readiness_for_promotion: string;
    suggested_roles: string[];
    skill_gaps: string[];
    development_plan: string[];
  };
  risk_assessment: {
    flight_risk: string;
    performance_risk: string;
    mitigation_strategies: string[];
  };
}

class AIService {
  /**
   * Generate AI-driven action plan templates
   */
  async generateActionPlans(issueType: string): Promise<AIActionPlan[]> {
    try {
      const response = await axios.post(`${API_BASE_URL}/ai/generate-action-plans`, null, {
        params: { issue_type: issueType }
      });
      return response.data.action_plans;
    } catch (error) {
      console.error('Error generating AI action plans:', error);
      throw new Error('Failed to generate AI action plans');
    }
  }

  /**
   * Analyze outliers using AI
   */
  async analyzeOutliers(): Promise<OutlierAnalysis> {
    try {
      const response = await axios.post(`${API_BASE_URL}/ai/analyze-outliers`);
      return response.data;
    } catch (error) {
      console.error('Error analyzing outliers:', error);
      throw new Error('Failed to analyze outliers');
    }
  }

  /**
   * Generate AI-optimized survey questions
   */
  async generateSurveyQuestions(kpiFocus: string, surveyType: string = 'pulse'): Promise<SurveyQuestion[]> {
    try {
      const response = await axios.post(`${API_BASE_URL}/ai/generate-survey-questions`, null, {
        params: { 
          kpi_focus: kpiFocus,
          survey_type: surveyType
        }
      });
      return response.data.questions;
    } catch (error) {
      console.error('Error generating survey questions:', error);
      throw new Error('Failed to generate survey questions');
    }
  }

  /**
   * Analyze action plan efficacy using AI
   */
  async analyzeActionPlanEfficacy(actionPlanId: number): Promise<EfficacyAnalysis> {
    try {
      const response = await axios.post(`${API_BASE_URL}/ai/analyze-action-plan-efficacy/${actionPlanId}`);
      return response.data;
    } catch (error) {
      console.error('Error analyzing action plan efficacy:', error);
      throw new Error('Failed to analyze action plan efficacy');
    }
  }

  /**
   * Generate performance insights for an employee
   */
  async generatePerformanceInsights(employeeId: number): Promise<PerformanceInsights> {
    try {
      const response = await axios.post(`${API_BASE_URL}/ai/performance-insights/${employeeId}`);
      return response.data;
    } catch (error) {
      console.error('Error generating performance insights:', error);
      throw new Error('Failed to generate performance insights');
    }
  }
}

export const aiService = new AIService(); 