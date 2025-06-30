import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'your-supabase-url';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-supabase-anon-key';

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Missing Supabase environment variables');
  console.error('VITE_SUPABASE_URL:', supabaseUrl);
  console.error('VITE_SUPABASE_ANON_KEY:', supabaseAnonKey ? 'Present' : 'Missing');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Database types for better TypeScript support
export type Database = {
  public: {
    Tables: {
      departments: {
        Row: {
          id: string;
          name: string;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          name: string;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          name?: string;
          created_at?: string;
          updated_at?: string;
        };
      };
      employees: {
        Row: {
          id: string;
          name: string;
          email: string;
          department_id: string;
          position: string;
          hire_date: string;
          status: string;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          name: string;
          email: string;
          department_id: string;
          position: string;
          hire_date: string;
          status: string;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          name?: string;
          email?: string;
          department_id?: string;
          position?: string;
          hire_date?: string;
          status?: string;
          created_at?: string;
          updated_at?: string;
        };
      };
      surveys: {
        Row: {
          id: string;
          title: string;
          description: string;
          type: string;
          status: string;
          created_at: string;
          end_date: string;
        };
        Insert: {
          id?: string;
          title: string;
          description: string;
          type: string;
          status: string;
          created_at?: string;
          end_date: string;
        };
        Update: {
          id?: string;
          title?: string;
          description?: string;
          type?: string;
          status?: string;
          created_at?: string;
          end_date?: string;
        };
      };
      survey_questions: {
        Row: {
          id: string;
          survey_id: string;
          text: string;
          type: string;
          options: any;
          created_at: string;
        };
        Insert: {
          id?: string;
          survey_id: string;
          text: string;
          type: string;
          options?: any;
          created_at?: string;
        };
        Update: {
          id?: string;
          survey_id?: string;
          text?: string;
          type?: string;
          options?: any;
          created_at?: string;
        };
      };
      performance_reviews: {
        Row: {
          id: string;
          employee_id: string;
          reviewer_id: string;
          rating: number;
          comments: string;
          status: string;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          employee_id: string;
          reviewer_id: string;
          rating: number;
          comments: string;
          status: string;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          employee_id?: string;
          reviewer_id?: string;
          rating?: number;
          comments?: string;
          status?: string;
          created_at?: string;
          updated_at?: string;
        };
      };
      performance_goals: {
        Row: {
          id: string;
          review_id: string;
          description: string;
          status: string;
          due_date: string;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          review_id: string;
          description: string;
          status: string;
          due_date: string;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          review_id?: string;
          description?: string;
          status?: string;
          due_date?: string;
          created_at?: string;
          updated_at?: string;
        };
      };
    };
  };
};

// Type definitions for our database tables
export type Department = {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
};

export type Employee = {
  id: string;
  name: string;
  email: string;
  department_id: string;
  position: string;
  hire_date: string;
  status: 'active' | 'inactive';
  created_at: string;
  updated_at: string;
};

export type Survey = {
  id: string;
  title: string;
  description: string | null;
  type: string;
  status: 'draft' | 'active' | 'completed';
  created_at: string;
  end_date: string;
};

export type SurveyQuestion = {
  id: string;
  survey_id: string;
  text: string;
  type: string;
  options: Record<string, any> | null;
  created_at: string;
};

export type PerformanceReview = {
  id: string;
  employee_id: string;
  reviewer_id: string;
  rating: number;
  comments: string | null;
  status: 'pending' | 'completed';
  created_at: string;
  updated_at: string;
};

export type PerformanceGoal = {
  id: string;
  review_id: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed';
  due_date: string;
  created_at: string;
  updated_at: string;
}; 