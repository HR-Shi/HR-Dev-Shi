import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../api';

interface Survey {
  id: string;
  title: string;
  description: string;
  type: 'baseline' | 'pulse' | 'annual' | 'exit' | 'onboarding' | 'custom';
  status: 'draft' | 'active' | 'completed' | 'scheduled';
  questions: SurveyQuestion[];
  target_audience: string[];
  department_filters: string[];
  response_rate: number;
  total_responses: number;
  created_at: string;
  updated_at: string;
  scheduled_date?: string;
  end_date: string;
  kpi_mappings: string[];
  ai_generated: boolean;
}

interface SurveyQuestion {
  id: string;
  question_text: string;
  question_type: 'multiple_choice' | 'rating' | 'text' | 'boolean' | 'matrix';
  options?: string[];
  required: boolean;
  ai_generated: boolean;
  kpi_category: string;
  weight: number;
}

interface SurveyResponse {
  id: string;
  survey_id: string;
  employee_id: string;
  responses: Record<string, any>;
  completed_at: string;
  time_taken: number;
}

interface SurveyAnalytics {
  response_rate: number;
  completion_rate: number;
  average_score: number;
  sentiment_breakdown: {
    positive: number;
    neutral: number;
    negative: number;
  };
  department_breakdown: Record<string, number>;
  question_analytics: Record<string, any>;
  kpi_correlations: Record<string, number>;
}

export function EnhancedSurveySystem() {
  const [surveys, setSurveys] = useState<Survey[]>([]);
  const [selectedSurvey, setSelectedSurvey] = useState<Survey | null>(null);
  const [analytics, setAnalytics] = useState<SurveyAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form states
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showAIQuestionGenerator, setShowAIQuestionGenerator] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: 'pulse' as Survey['type'],
    target_audience: [] as string[],
    department_filters: [] as string[],
    end_date: '',
    kpi_mappings: [] as string[]
  });
  
  // AI Question Generation
  const [aiQuestionsLoading, setAiQuestionsLoading] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState<SurveyQuestion[]>([]);
  const [selectedKPIs, setSelectedKPIs] = useState<string[]>([]);
  const [questionObjectives, setQuestionObjectives] = useState<string[]>([]);

  const surveyTypes = [
    { value: 'baseline', label: 'Baseline Survey', description: 'Comprehensive initial assessment' },
    { value: 'pulse', label: 'Pulse Survey', description: 'Quick regular check-ins (5-10 questions)' },
    { value: 'annual', label: 'Annual Survey', description: 'Comprehensive yearly assessment' },
    { value: 'exit', label: 'Exit Interview', description: 'Departing employee feedback' },
    { value: 'onboarding', label: 'Onboarding Survey', description: 'New employee experience' },
    { value: 'custom', label: 'Custom Survey', description: 'Tailored for specific needs' }
  ];

  const kpiCategories = [
    'Employee Engagement',
    'Job Satisfaction',
    'Work-Life Balance',
    'Career Development',
    'Management Effectiveness',
    'Team Collaboration',
    'Workplace Culture',
    'Performance Recognition',
    'Communication Effectiveness',
    'Innovation & Creativity'
  ];

  const departments = ['All', 'Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations', 'Customer Success'];

  useEffect(() => {
    fetchSurveys();
  }, []);

  const fetchSurveys = async () => {
    try {
      setLoading(true);
      const data = await dashboardAPI.getSurveys();
      setSurveys(data || []);
    } catch (error) {
      console.error('Error fetching surveys:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSurveyAnalytics = async (surveyId: string) => {
    try {
      const data = await dashboardAPI.getSurveyAnalytics(surveyId);
      setAnalytics(data);
    } catch (error) {
      console.error('Error fetching survey analytics:', error);
    }
  };

  const generateAIQuestions = async () => {
    try {
      setAiQuestionsLoading(true);
      const questions = await dashboardAPI.generateAISurveyQuestions({
        survey_type: formData.type,
        kpi_categories: selectedKPIs,
        objectives: questionObjectives,
        target_audience: formData.target_audience,
        question_count: formData.type === 'pulse' ? 8 : 20
      });
      
      setGeneratedQuestions(questions);
    } catch (error) {
      console.error('Error generating AI questions:', error);
      setError('Failed to generate AI questions');
    } finally {
      setAiQuestionsLoading(false);
    }
  };

  const createSurvey = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const surveyData = {
        ...formData,
        questions: generatedQuestions,
        status: 'draft' as const,
        ai_generated: generatedQuestions.length > 0
      };
      
      const newSurvey = await dashboardAPI.createSurvey(surveyData);
      setSurveys(prev => [...prev, newSurvey]);
      setShowCreateForm(false);
      resetForm();
    } catch (error) {
      console.error('Error creating survey:', error);
      setError('Failed to create survey');
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      type: 'pulse',
      target_audience: [],
      department_filters: [],
      end_date: '',
      kpi_mappings: []
    });
    setGeneratedQuestions([]);
    setSelectedKPIs([]);
    setQuestionObjectives([]);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'draft': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      case 'scheduled': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'baseline': return '📊';
      case 'pulse': return '💓';
      case 'annual': return '📅';
      case 'exit': return '👋';
      case 'onboarding': return '🚀';
      case 'custom': return '🎯';
      default: return '📋';
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">📋 Enhanced Survey System</h1>
          <p className="text-gray-600">AI-powered survey creation with real-time analytics and KPI integration</p>
        </div>
        <button 
          onClick={() => setShowCreateForm(true)}
          className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors flex items-center"
        >
          <span className="mr-2">+</span>
          Create Survey
        </button>
      </div>

      {/* Survey Analytics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <span className="text-2xl">📊</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600">Total Surveys</h3>
              <p className="text-2xl font-bold text-gray-900">{surveys.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <span className="text-2xl">✅</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600">Active Surveys</h3>
              <p className="text-2xl font-bold text-green-600">
                {surveys.filter(s => s.status === 'active').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <span className="text-2xl">🤖</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600">AI Generated</h3>
              <p className="text-2xl font-bold text-purple-600">
                {surveys.filter(s => s.ai_generated).length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-orange-100 rounded-lg">
              <span className="text-2xl">📈</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600">Avg Response Rate</h3>
              <p className="text-2xl font-bold text-orange-600">
                {surveys.length > 0 
                  ? Math.round(surveys.reduce((sum, s) => sum + s.response_rate, 0) / surveys.length)
                  : 0
                }%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Surveys List */}
      <div className="space-y-6">
        {surveys.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
              <span className="text-4xl">📋</span>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No surveys created yet</h3>
            <p className="text-gray-600 mb-4">Create your first survey using AI-powered question generation.</p>
            <button 
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Your First Survey
            </button>
          </div>
        ) : (
          surveys.map((survey) => (
            <div key={survey.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-xl font-semibold text-gray-900">{survey.title}</h3>
                    <span className="px-3 py-1 text-sm font-medium rounded-full bg-blue-100 text-blue-800">
                      {survey.status.toUpperCase()}
                    </span>
                    {survey.ai_generated && (
                      <span className="px-3 py-1 text-sm font-medium rounded-full bg-purple-100 text-purple-800">
                        🤖 AI GENERATED
                      </span>
                    )}
                  </div>
                  <p className="text-gray-700 mb-4">{survey.description}</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                      <h4 className="text-sm font-medium text-gray-600">Questions</h4>
                      <p className="text-2xl font-bold text-gray-900">{survey.questions?.length || 0}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                      <h4 className="text-sm font-medium text-gray-600">Responses</h4>
                      <p className="text-2xl font-bold text-blue-600">{survey.total_responses || 0}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                      <h4 className="text-sm font-medium text-gray-600">Response Rate</h4>
                      <p className="text-2xl font-bold text-green-600">{survey.response_rate || 0}%</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* AI Question Generator Modal */}
      {showAIQuestionGenerator && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">🤖 AI Question Generator</h2>
                <button
                  onClick={() => setShowAIQuestionGenerator(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Survey Type</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as Survey['type'] }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {surveyTypes.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Target Departments</label>
                  <select
                    multiple
                    value={formData.department_filters}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      department_filters: Array.from(e.target.selectedOptions, option => option.value)
                    }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {departments.map(dept => (
                      <option key={dept} value={dept}>{dept}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">KPI Categories to Focus On</label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {kpiCategories.map(category => (
                    <label key={category} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                      <input
                        type="checkbox"
                        checked={selectedKPIs.includes(category)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedKPIs(prev => [...prev, category]);
                          } else {
                            setSelectedKPIs(prev => prev.filter(k => k !== category));
                          }
                        }}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm font-medium text-gray-900">{category}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Additional Objectives (Optional)</label>
                <textarea
                  placeholder="e.g., Focus on remote work challenges, leadership effectiveness, career development opportunities..."
                  value={questionObjectives.join('\n')}
                  onChange={(e) => setQuestionObjectives(e.target.value.split('\n').filter(o => o.trim()))}
                  rows={3}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowAIQuestionGenerator(false)}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={generateAIQuestions}
                  disabled={aiQuestionsLoading || selectedKPIs.length === 0}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {aiQuestionsLoading ? 'Generating...' : 'Generate Questions'}
                </button>
              </div>

              {/* Generated Questions Preview */}
              {generatedQuestions.length > 0 && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Generated Questions Preview</h3>
                  <div className="space-y-3">
                    {generatedQuestions.slice(0, 5).map((question, index) => (
                      <div key={index} className="bg-white p-3 rounded-lg">
                        <p className="text-sm font-medium text-gray-900">{question.question_text}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          Type: {question.question_type} | Category: {question.kpi_category}
                        </p>
                      </div>
                    ))}
                    {generatedQuestions.length > 5 && (
                      <p className="text-sm text-gray-600">...and {generatedQuestions.length - 5} more questions</p>
                    )}
                  </div>
                  <button
                    onClick={() => {
                      setShowAIQuestionGenerator(false);
                      setShowCreateForm(true);
                    }}
                    className="mt-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    Use These Questions
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Create Survey Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto m-4">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">Create New Survey</h2>
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
            </div>

            <form onSubmit={createSurvey} className="p-6 space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Survey Title</label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Q1 2024 Employee Engagement Survey"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  required
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  rows={3}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Describe the purpose and goals of this survey..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Survey Type</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as Survey['type'] }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {surveyTypes.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
                  <input
                    type="date"
                    required
                    value={formData.end_date}
                    onChange={(e) => setFormData(prev => ({ ...prev, end_date: e.target.value }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {generatedQuestions.length > 0 && (
                <div className="p-4 bg-green-50 rounded-lg">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Generated Questions</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    {generatedQuestions.length} questions have been generated and will be included in this survey.
                  </p>
                  <div className="max-h-48 overflow-y-auto space-y-2">
                    {generatedQuestions.map((question, index) => (
                      <div key={index} className="bg-white p-2 rounded text-sm">
                        <strong>Q{index + 1}:</strong> {question.question_text}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  Create Survey
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
} 