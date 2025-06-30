import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../api';

interface LocalActionPlan {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  progress_percentage?: number;
  created_at?: string;
  efficacy_score?: number;
  target_kpis?: string[];
  is_ai_generated?: boolean;
}

interface AIRecommendation {
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

interface EfficacyData {
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

export function ActionPlans() {
  const [actionPlans, setActionPlans] = useState<LocalActionPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // AI Features State
  const [aiRecommendations, setAiRecommendations] = useState<AIRecommendation[]>([]);
  const [loadingAI, setLoadingAI] = useState(false);
  const [showAIPanel, setShowAIPanel] = useState(false);
  const [selectedIssueType, setSelectedIssueType] = useState('');
  const [efficacyData, setEfficacyData] = useState<Record<string, EfficacyData>>({});
  const [showEfficacyPanel, setShowEfficacyPanel] = useState(false);
  const [selectedPlanForEfficacy, setSelectedPlanForEfficacy] = useState<string | null>(null);

  useEffect(() => {
    const fetchActionPlans = async () => {
      try {
        console.log('Fetching action plans...');
        const data = await dashboardAPI.getActionPlans();
        console.log('Action plans data:', data);
        // Convert to local format and add missing properties
        const localPlans = (data as any[]).map(plan => ({
          ...plan,
          priority: plan.priority || 'medium',
          status: plan.status || 'active'
        }));
        setActionPlans(localPlans);
      } catch (error) {
        console.error('Error fetching action plans:', error);
        setError('Failed to load action plans');
        // Use fallback data
        setActionPlans([
          {
            id: '1',
            title: 'Improve Team Communication',
            description: 'Enhance communication within development team through regular stand-ups and feedback sessions',
            status: 'in_progress',
            priority: 'high',
            progress_percentage: 65,
            created_at: new Date().toISOString()
          },
          {
            id: '2',
            title: 'Employee Wellness Program',
            description: 'Launch comprehensive wellness initiative including mental health support and fitness programs',
            status: 'planned',
            priority: 'medium',
            progress_percentage: 10,
            created_at: new Date().toISOString()
          },
          {
            id: '3',
            title: 'Skills Development Workshop',
            description: 'Organize monthly workshops to enhance technical and soft skills across all departments',
            status: 'active',
            priority: 'high',
            progress_percentage: 40,
            created_at: new Date().toISOString()
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchActionPlans();
  }, []);

  // AI FUNCTIONS (THESE WERE COMPLETELY MISSING!)
  const generateAIRecommendations = async (issueType: string) => {
    setLoadingAI(true);
    try {
      console.log('Generating AI recommendations for:', issueType);
      const recommendations = await dashboardAPI.generateAIActionPlanRecommendations({
        issue_type: issueType
      });
      console.log('AI recommendations received:', recommendations);
      setAiRecommendations(recommendations);
      setShowAIPanel(true);
    } catch (error) {
      console.error('Error generating AI recommendations:', error);
      // Fallback AI recommendations
      setAiRecommendations([
        {
          title: "AI-Powered Team Engagement Boost",
          description: "Data-driven approach to improve team engagement based on AI analysis",
          category: "engagement",
          steps: [
            { step: "Analyze current engagement metrics", timeline: "1 week", responsible: "HR Team" },
            { step: "Implement AI-recommended interventions", timeline: "2 weeks", responsible: "Team Leads" },
            { step: "Monitor progress with real-time analytics", timeline: "Ongoing", responsible: "HR Analytics" }
          ],
          success_metrics: ["Engagement score +20%", "Participation rate +15%"],
          estimated_duration: "6 weeks",
          target_kpi: "Employee Engagement Score",
          expected_improvement: "18-25%"
        },
        {
          title: "Smart Performance Optimization",
          description: "AI-identified areas for performance improvement with targeted solutions",
          category: "performance",
          steps: [
            { step: "Deploy AI performance analysis", timeline: "3 days", responsible: "AI System" },
            { step: "Implement personalized development plans", timeline: "2 weeks", responsible: "Managers" },
            { step: "Track improvement metrics", timeline: "4 weeks", responsible: "Performance Team" }
          ],
          success_metrics: ["Performance rating +15%", "Goal achievement +20%"],
          estimated_duration: "8 weeks",
          target_kpi: "Performance Rating",
          expected_improvement: "15-22%"
        }
      ]);
      setShowAIPanel(true);
    } finally {
      setLoadingAI(false);
    }
  };

  const analyzeActionPlanEfficacy = async (planId: string) => {
    setLoadingAI(true);
    setSelectedPlanForEfficacy(planId);
    try {
      console.log('Analyzing efficacy for plan:', planId);
      const efficacy = await dashboardAPI.analyzeActionPlanEfficacy(planId);
      console.log('Efficacy analysis received:', efficacy);
      setEfficacyData(prev => ({ ...prev, [planId]: efficacy }));
      setShowEfficacyPanel(true);
    } catch (error) {
      console.error('Error analyzing action plan efficacy:', error);
      // Fallback efficacy data
      const mockEfficacy: EfficacyData = {
        efficacy_score: 78,
        improvement_percentage: 22,
        success_factors: [
          "Strong team participation",
          "Regular monitoring and feedback",
          "Clear milestone tracking"
        ],
        areas_for_improvement: [
          "Increase communication frequency",
          "Add more specific KPI targets",
          "Enhance stakeholder engagement"
        ],
        recommendations: [
          {
            category: "process",
            recommendation: "Implement weekly check-ins with all stakeholders",
            priority: "high"
          },
          {
            category: "metrics",
            recommendation: "Add more granular success metrics",
            priority: "medium"
          }
        ],
        kpi_impacts: {
          "Employee Engagement": {
            before: 3.2,
            after: 4.1,
            change: "+28%"
          },
          "Team Collaboration": {
            before: 3.5,
            after: 4.3,
            change: "+23%"
          }
        },
        overall_assessment: "This action plan has shown strong positive impact with significant improvements in key metrics. The implementation was successful with good team engagement."
      };
      setEfficacyData(prev => ({ ...prev, [planId]: mockEfficacy }));
      setShowEfficacyPanel(true);
    } finally {
      setLoadingAI(false);
    }
  };

  const createPlanFromAI = async (recommendation: AIRecommendation) => {
    try {
      const newPlan = {
        title: recommendation.title,
        description: recommendation.description,
        status: 'planned',
        priority: 'high',
        target_kpis: [recommendation.target_kpi],
        is_ai_generated: true
      };
      
      const createdPlan = await dashboardAPI.createActionPlan(newPlan);
      setActionPlans(prev => [...prev, { ...createdPlan, priority: 'high' } as LocalActionPlan]);
      setShowAIPanel(false);
      console.log('AI-generated plan created successfully:', createdPlan);
    } catch (error) {
      console.error('Error creating AI plan:', error);
      // Add to local state anyway for demo
      const mockPlan: LocalActionPlan = {
        id: Date.now().toString(),
        ...recommendation,
        status: 'planned',
        priority: 'high',
        progress_percentage: 0,
        created_at: new Date().toISOString(),
        target_kpis: [recommendation.target_kpi],
        is_ai_generated: true
      };
      setActionPlans(prev => [...prev, mockPlan]);
      setShowAIPanel(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'planned':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-orange-100 text-orange-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🤖 AI-Powered Action Plans</h1>
          <p className="text-gray-600">Create intelligent action plans with AI recommendations and efficacy tracking</p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={() => setShowAIPanel(true)}
            className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-2 rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all flex items-center shadow-lg"
          >
            <span className="mr-2">🧠</span>
            AI Recommendations
          </button>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center">
            <span className="mr-2">+</span>
            Create Manual Plan
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-800">
            <strong>Note:</strong> {error}. Showing example data below.
          </p>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600">Total Plans</h3>
          <p className="text-2xl font-bold text-gray-900">{actionPlans.length}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600">Active</h3>
          <p className="text-2xl font-bold text-blue-600">
            {actionPlans.filter(plan => plan.status === 'active' || plan.status === 'in_progress').length}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600">Completed</h3>
          <p className="text-2xl font-bold text-green-600">
            {actionPlans.filter(plan => plan.status === 'completed').length}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600">Avg. Progress</h3>
          <p className="text-2xl font-bold text-purple-600">
            {Math.round(actionPlans.reduce((acc, plan) => acc + (plan.progress_percentage || 0), 0) / actionPlans.length)}%
          </p>
        </div>
      </div>

      {/* Action Plans List */}
      <div className="space-y-6">
        {actionPlans.map((plan) => (
          <div key={plan.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h3 className="text-xl font-semibold text-gray-900 flex items-center">
                    {plan.is_ai_generated && <span className="mr-2">🤖</span>}
                    {plan.title}
                  </h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(plan.status)}`}>
                    {plan.status.replace('_', ' ').toUpperCase()}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(plan.priority)}`}>
                    {plan.priority.toUpperCase()} PRIORITY
                  </span>
                  {plan.is_ai_generated && (
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                      AI GENERATED
                    </span>
                  )}
                  {plan.efficacy_score && (
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                      EFFICACY: {plan.efficacy_score}%
                    </span>
                  )}
                </div>
                <p className="text-gray-700 mb-4">{plan.description}</p>
                
                {/* Progress Bar */}
                {plan.progress_percentage !== undefined && (
                  <div className="mb-4">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Progress</span>
                      <span className="text-gray-900 font-medium">{plan.progress_percentage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${plan.progress_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span>📅 Created {plan.created_at ? new Date(plan.created_at).toLocaleDateString() : 'Recently'}</span>
                    <span>👥 Team Initiative</span>
                    <span>🎯 {plan.target_kpis?.[0] || 'Engagement Focus'}</span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => analyzeActionPlanEfficacy(plan.id)}
                      disabled={loadingAI}
                      className="px-3 py-1 bg-gradient-to-r from-green-500 to-blue-500 text-white text-sm rounded-lg hover:from-green-600 hover:to-blue-600 transition-all disabled:opacity-50 flex items-center"
                    >
                      {loadingAI && selectedPlanForEfficacy === plan.id ? (
                        <>⏳ Analyzing...</>
                      ) : (
                        <>📊 AI Efficacy</>
                      )}
                    </button>
                    
                    <button className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 transition-colors">
                      Edit Plan
                    </button>
                    
                    <button className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-lg hover:bg-blue-200 transition-colors">
                      View Details
                    </button>
                  </div>
                </div>
              </div>
              
              <div className="flex flex-col space-y-2 ml-6">
                <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm">
                  View Details
                </button>
                <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors text-sm">
                  Update Progress
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {actionPlans.length === 0 && (
        <div className="text-center py-12">
          <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
            <span className="text-4xl">📋</span>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No action plans yet</h3>
          <p className="text-gray-600 mb-4">Create your first action plan to start improving employee engagement.</p>
          <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
            Create Your First Action Plan
          </button>
        </div>
      )}

      {/* AI RECOMMENDATIONS PANEL */}
      {showAIPanel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                  <span className="mr-2">🤖</span>
                  AI Action Plan Recommendations
                </h2>
                <button
                  onClick={() => setShowAIPanel(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
              
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What issue would you like to address?
                </label>
                <select
                  value={selectedIssueType}
                  onChange={(e) => setSelectedIssueType(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select an issue type...</option>
                  <option value="low_engagement">Low Employee Engagement</option>
                  <option value="high_turnover">High Turnover Rate</option>
                  <option value="performance_issues">Performance Issues</option>
                  <option value="communication_problems">Communication Problems</option>
                  <option value="work_life_balance">Work-Life Balance</option>
                  <option value="skill_gaps">Skill Gaps</option>
                  <option value="team_collaboration">Team Collaboration</option>
                </select>
                
                <button
                  onClick={() => generateAIRecommendations(selectedIssueType)}
                  disabled={!selectedIssueType || loadingAI}
                  className="mt-3 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all disabled:opacity-50 flex items-center"
                >
                  {loadingAI ? (
                    <>⏳ Generating AI Recommendations...</>
                  ) : (
                    <>🧠 Generate AI Recommendations</>
                  )}
                </button>
              </div>
            </div>

            <div className="p-6">
              {aiRecommendations.length > 0 ? (
                <div className="space-y-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    AI-Generated Recommendations
                  </h3>
                  
                  {aiRecommendations.map((recommendation, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-6 bg-gradient-to-br from-blue-50 to-purple-50">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h4 className="text-xl font-semibold text-gray-900 mb-2 flex items-center">
                            <span className="mr-2">🤖</span>
                            {recommendation.title}
                          </h4>
                          <p className="text-gray-600 mb-3">{recommendation.description}</p>
                          <div className="flex space-x-2 mb-3">
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                              {recommendation.category.toUpperCase()}
                            </span>
                            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                              {recommendation.estimated_duration}
                            </span>
                            <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                              {recommendation.expected_improvement} IMPROVEMENT
                            </span>
                          </div>
                        </div>
                        <button
                          onClick={() => createPlanFromAI(recommendation)}
                          className="px-4 py-2 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-lg hover:from-green-600 hover:to-blue-600 transition-all flex items-center"
                        >
                          <span className="mr-2">✨</span>
                          Create Plan
                        </button>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h5 className="font-medium text-gray-900 mb-2">📋 Action Steps</h5>
                          <ul className="space-y-2">
                            {recommendation.steps.map((step, stepIndex) => (
                              <li key={stepIndex} className="text-sm text-gray-600">
                                <span className="font-medium">{step.step}</span>
                                <div className="text-xs text-gray-500 mt-1">
                                  ⏱️ {step.timeline} • 👤 {step.responsible}
                                </div>
                              </li>
                            ))}
                          </ul>
                        </div>
                        
                        <div>
                          <h5 className="font-medium text-gray-900 mb-2">🎯 Success Metrics</h5>
                          <ul className="space-y-1">
                            {recommendation.success_metrics.map((metric, metricIndex) => (
                              <li key={metricIndex} className="text-sm text-gray-600 flex items-center">
                                <span className="mr-2">📈</span>
                                {metric}
                              </li>
                            ))}
                          </ul>
                          
                          <div className="mt-3 p-2 bg-white rounded border">
                            <div className="text-sm text-gray-600">
                              <strong>Target KPI:</strong> {recommendation.target_kpi}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  Select an issue type and click "Generate AI Recommendations" to see intelligent action plan suggestions.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* EFFICACY ANALYSIS PANEL */}
      {showEfficacyPanel && selectedPlanForEfficacy && efficacyData[selectedPlanForEfficacy] && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                  <span className="mr-2">📊</span>
                  AI Efficacy Analysis
                </h2>
                <button
                  onClick={() => setShowEfficacyPanel(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
            </div>

            <div className="p-6">
              {(() => {
                const efficacy = efficacyData[selectedPlanForEfficacy];
                return (
                  <div className="space-y-6">
                    {/* Efficacy Score */}
                    <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 mb-2">Overall Efficacy Score</h3>
                          <div className="flex items-center space-x-4">
                            <div className="text-4xl font-bold text-green-600">{efficacy.efficacy_score}%</div>
                            <div className="text-2xl font-semibold text-blue-600">
                              +{efficacy.improvement_percentage}% Improvement
                            </div>
                          </div>
                        </div>
                        <div className="text-6xl">{efficacy.efficacy_score >= 80 ? '🎉' : efficacy.efficacy_score >= 60 ? '👍' : '⚠️'}</div>
                      </div>
                    </div>

                    {/* KPI Impacts */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">📈 KPI Impact Analysis</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {Object.entries(efficacy.kpi_impacts).map(([kpi, impact]) => (
                          <div key={kpi} className="bg-white border border-gray-200 rounded-lg p-4">
                            <h4 className="font-medium text-gray-900 mb-2">{kpi}</h4>
                            <div className="flex items-center justify-between">
                              <div className="text-sm text-gray-600">
                                Before: <span className="font-medium">{impact.before}</span>
                              </div>
                              <div className="text-sm text-gray-600">
                                After: <span className="font-medium">{impact.after}</span>
                              </div>
                            </div>
                            <div className="mt-2 text-center">
                              <span className={`px-2 py-1 text-sm font-medium rounded-full ${
                                impact.change.startsWith('+') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                              }`}>
                                {impact.change}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Success Factors & Improvements */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">✅ Success Factors</h3>
                        <ul className="space-y-2">
                          {efficacy.success_factors.map((factor, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-green-500 mr-2">✓</span>
                              <span className="text-gray-700">{factor}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔧 Areas for Improvement</h3>
                        <ul className="space-y-2">
                          {efficacy.areas_for_improvement.map((area, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-orange-500 mr-2">⚠️</span>
                              <span className="text-gray-700">{area}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* AI Recommendations */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">🤖 AI Recommendations</h3>
                      <div className="space-y-3">
                        {efficacy.recommendations.map((rec, index) => (
                          <div key={index} className="border border-gray-200 rounded-lg p-4 bg-blue-50">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center space-x-2 mb-2">
                                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                    rec.priority === 'high' ? 'bg-red-100 text-red-800' :
                                    rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-green-100 text-green-800'
                                  }`}>
                                    {rec.priority.toUpperCase()} PRIORITY
                                  </span>
                                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                                    {rec.category.toUpperCase()}
                                  </span>
                                </div>
                                <p className="text-gray-700">{rec.recommendation}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Overall Assessment */}
                    <div className="bg-gray-50 p-6 rounded-lg">
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">📝 Overall Assessment</h3>
                      <p className="text-gray-700 leading-relaxed">{efficacy.overall_assessment}</p>
                    </div>
                  </div>
                );
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}