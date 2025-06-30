import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { aiService, AIActionPlan, OutlierAnalysis, SurveyQuestion, EfficacyAnalysis, PerformanceInsights } from '../services/aiService';
import { 
  Psychology as Brain,
  AutoAwesome as Sparkles,
  TrendingUp,
  People as Users,
  Assessment,
  QuestionAnswer,
  Insights,
  Warning as AlertTriangle
} from '@mui/icons-material';

export function AIDemo() {
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [results, setResults] = useState<Record<string, any>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  const setLoadingState = (key: string, isLoading: boolean) => {
    setLoading(prev => ({ ...prev, [key]: isLoading }));
  };

  const setResult = (key: string, result: any) => {
    setResults(prev => ({ ...prev, [key]: result }));
  };

  const setError = (key: string, error: string) => {
    setErrors(prev => ({ ...prev, [key]: error }));
  };

  const generateActionPlans = async (issueType: string) => {
    const key = `actionPlans_${issueType}`;
    setLoadingState(key, true);
    setError(key, '');
    try {
      const plans = await aiService.generateActionPlans(issueType);
      setResult(key, plans);
    } catch (error) {
      setError(key, 'Failed to generate action plans');
    } finally {
      setLoadingState(key, false);
    }
  };

  const analyzeOutliers = async () => {
    const key = 'outliers';
    setLoadingState(key, true);
    setError(key, '');
    try {
      const analysis = await aiService.analyzeOutliers();
      setResult(key, analysis);
    } catch (error) {
      setError(key, 'Failed to analyze outliers');
    } finally {
      setLoadingState(key, false);
    }
  };

  const generateSurveyQuestions = async (kpiFocus: string) => {
    const key = `survey_${kpiFocus}`;
    setLoadingState(key, true);
    setError(key, '');
    try {
      const questions = await aiService.generateSurveyQuestions(kpiFocus, 'pulse');
      setResult(key, questions);
    } catch (error) {
      setError(key, 'Failed to generate survey questions');
    } finally {
      setLoadingState(key, false);
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
          <Brain className="w-8 h-8 text-purple-500 mr-3" />
          AI Features Demo
        </h1>
        <p className="text-gray-600">
          Explore the AI-powered features integrated into the HR Dashboard using Cerebras API
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* AI Action Plans */}
        <Card>
          <div className="flex items-center mb-4">
            <Sparkles className="w-5 h-5 text-purple-500 mr-2" />
            <h3 className="text-lg font-semibold">AI Action Plan Generation</h3>
          </div>
          <p className="text-gray-600 mb-4">Generate targeted action plans based on specific issues</p>
          
          <div className="space-y-3 mb-4">
            <Button 
              onClick={() => generateActionPlans('low_engagement')}
              disabled={loading['actionPlans_low_engagement']}
              className="w-full"
            >
              {loading['actionPlans_low_engagement'] && <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>}
              Generate for Low Engagement
            </Button>
            <Button 
              onClick={() => generateActionPlans('performance_issues')}
              disabled={loading['actionPlans_performance_issues']}
              variant="outline"
              className="w-full"
            >
              {loading['actionPlans_performance_issues'] && <div className="w-4 h-4 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mr-2"></div>}
              Generate for Performance Issues
            </Button>
          </div>

          {errors['actionPlans_low_engagement'] && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
              <p className="text-red-700 text-sm">{errors['actionPlans_low_engagement']}</p>
            </div>
          )}

          {results['actionPlans_low_engagement'] && (
            <div className="space-y-4">
              {results['actionPlans_low_engagement'].map((plan: AIActionPlan, index: number) => (
                <div key={index} className="p-4 border border-purple-200 rounded-lg bg-purple-50">
                  <h4 className="font-semibold text-gray-900 mb-2">{plan.title}</h4>
                  <p className="text-sm text-gray-700 mb-3">{plan.description}</p>
                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div>
                      <span className="font-medium">Category:</span> {plan.category}
                    </div>
                    <div>
                      <span className="font-medium">Target KPI:</span> {plan.target_kpi}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Outlier Analysis */}
        <Card>
          <div className="flex items-center mb-4">
            <AlertTriangle className="w-5 h-5 text-orange-500 mr-2" />
            <h3 className="text-lg font-semibold">AI Outlier Analysis</h3>
          </div>
          <p className="text-gray-600 mb-4">Identify employees who need targeted interventions</p>
          
          <Button 
            onClick={analyzeOutliers}
            disabled={loading['outliers']}
            className="w-full mb-4"
          >
            {loading['outliers'] && <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>}
            Analyze Employee Outliers
          </Button>

          {errors['outliers'] && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
              <p className="text-red-700 text-sm">{errors['outliers']}</p>
            </div>
          )}

          {results['outliers'] && (
            <div className="space-y-4">
              {results['outliers'].insights?.map((insight: any, index: number) => (
                <div key={index} className="p-3 border border-blue-200 rounded bg-blue-50">
                  <p className="font-medium">{insight.category}</p>
                  <p className="text-sm">{insight.finding}</p>
                  <p className="text-sm text-blue-600">Recommendation: {insight.recommendation}</p>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Survey Question Generation */}
        <Card>
          <div className="flex items-center mb-4">
            <QuestionAnswer className="w-5 h-5 text-green-500 mr-2" />
            <h3 className="text-lg font-semibold">AI Survey Questions</h3>
          </div>
          <p className="text-gray-600 mb-4">Generate optimized survey questions for specific KPIs</p>
          
          <div className="space-y-3 mb-4">
            <Button 
              onClick={() => generateSurveyQuestions('Employee Engagement')}
              disabled={loading['survey_Employee Engagement']}
              className="w-full"
            >
              {loading['survey_Employee Engagement'] && <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>}
              Generate for Engagement
            </Button>
          </div>

          {results['survey_Employee Engagement'] && (
            <div className="space-y-3">
              {results['survey_Employee Engagement'].map((q: SurveyQuestion, index: number) => (
                <div key={index} className="p-3 border border-green-200 rounded bg-green-50">
                  <p className="font-medium mb-1">{q.question}</p>
                  <div className="text-xs text-gray-600">
                    <span>Type: {q.type}</span> | <span>KPI: {q.kpi_mapping}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Instructions */}
        <Card>
          <h3 className="text-lg font-semibold mb-4">Setup Instructions</h3>
          <div className="space-y-2 text-sm text-gray-600">
            <p>1. Set the <code className="bg-gray-100 px-1 rounded">CEREBRAS_API_KEY</code> in your backend environment</p>
            <p>2. Start the backend server: <code className="bg-gray-100 px-1 rounded">cd backend && python main.py</code></p>
            <p>3. Install the Cerebras SDK: <code className="bg-gray-100 px-1 rounded">pip install cerebras-cloud-sdk</code></p>
            <p>4. The AI features will use fallback responses if the API is not available</p>
          </div>
        </Card>
      </div>
    </div>
  );
} 