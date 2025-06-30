import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../api';

interface Employee {
  id: string;
  name: string;
  email: string;
  department: string;
  position: string;
  performance_score: number;
  engagement_score: number;
  satisfaction_score: number;
  last_review_date: string;
  hire_date: string;
}

interface OutlierResult {
  employee_id: string;
  employee_name: string;
  department: string;
  position: string;
  outlier_type: 'positive' | 'negative' | 'neutral';
  outlier_severity: 'low' | 'medium' | 'high' | 'critical';
  metrics: {
    performance_score: number;
    engagement_score: number;
    satisfaction_score: number;
    deviation_score: number;
  };
  ai_analysis: {
    risk_factors: string[];
    strengths: string[];
    recommendations: string[];
    intervention_priority: number;
    predicted_outcome: string;
  };
  detection_method: string;
  confidence_score: number;
  detected_at: string;
}

interface OutlierSummary {
  total_outliers: number;
  positive_outliers: number;
  negative_outliers: number;
  critical_outliers: number;
  departments_affected: number;
  average_confidence: number;
  trend_direction: 'improving' | 'declining' | 'stable';
}

export function OutlierDetection() {
  const [outliers, setOutliers] = useState<OutlierResult[]>([]);
  const [summary, setSummary] = useState<OutlierSummary | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Filter states
  const [selectedDepartment, setSelectedDepartment] = useState<string>('');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('');
  const [confidenceThreshold, setConfidenceThreshold] = useState<number>(0.7);
  
  // Detection settings
  const [detectionMethod, setDetectionMethod] = useState<string>('isolation_forest');
  const [customThreshold, setCustomThreshold] = useState<number>(2.0);
  const [metrics, setMetrics] = useState<string[]>(['performance_score', 'engagement_score', 'satisfaction_score']);
  
  const departments = ['All', 'Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations'];
  const severityLevels = ['All', 'low', 'medium', 'high', 'critical'];
  const outlierTypes = ['All', 'positive', 'negative', 'neutral'];
  
  const detectionMethods = [
    { value: 'isolation_forest', label: 'Isolation Forest (AI)', description: 'Advanced ML-based anomaly detection' },
    { value: 'statistical_zscore', label: 'Z-Score Analysis', description: 'Statistical outlier detection using standard deviations' },
    { value: 'interquartile_range', label: 'IQR Method', description: 'Quartile-based outlier identification' },
    { value: 'dbscan_clustering', label: 'DBSCAN Clustering', description: 'Density-based spatial clustering' },
    { value: 'local_outlier_factor', label: 'Local Outlier Factor', description: 'Local density-based outlier detection' }
  ];

  const availableMetrics = [
    { value: 'performance_score', label: 'Performance Score', category: 'Performance' },
    { value: 'engagement_score', label: 'Engagement Score', category: 'Engagement' },
    { value: 'satisfaction_score', label: 'Job Satisfaction', category: 'Satisfaction' },
    { value: 'productivity_score', label: 'Productivity Score', category: 'Performance' },
    { value: 'collaboration_score', label: 'Collaboration Score', category: 'Teamwork' },
    { value: 'innovation_score', label: 'Innovation Score', category: 'Creativity' },
    { value: 'leadership_score', label: 'Leadership Score', category: 'Leadership' },
    { value: 'learning_score', label: 'Learning & Development', category: 'Growth' }
  ];

  useEffect(() => {
    fetchEmployees();
    fetchOutlierSummary();
  }, []);

  const fetchEmployees = async () => {
    try {
      const data = await dashboardAPI.getEmployees();
      setEmployees(data);
    } catch (error) {
      console.error('Error fetching employees:', error);
      setError('Failed to load employee data');
    }
  };

  const fetchOutlierSummary = async () => {
    try {
      const data = await dashboardAPI.getOutlierSummary({
        department_id: selectedDepartment || undefined,
        severity: selectedSeverity || undefined
      });
      setSummary(data);
    } catch (error) {
      console.error('Error fetching outlier summary:', error);
    }
  };

  const detectOutliers = async () => {
    try {
      setAnalyzing(true);
      setError(null);
      
      const results = await dashboardAPI.detectAnalyticsOutliers({
        method: detectionMethod,
        threshold: customThreshold,
        department_id: selectedDepartment || undefined,
        metric_type: metrics.join(',')
      });
      
      // Process results and add AI analysis
      const processedResults = await Promise.all(
        results.map(async (result: any) => ({
          ...result,
          ai_analysis: await generateAIAnalysis(result)
        }))
      );
      
      setOutliers(processedResults);
      await fetchOutlierSummary();
      
    } catch (error) {
      console.error('Error detecting outliers:', error);
      setError('Failed to detect outliers. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const generateAIAnalysis = async (outlierResult: any): Promise<any> => {
    try {
      // This would integrate with the AI service for real analysis
      const response = await dashboardAPI.analyzeOutliersWithAI({
        employee_data: outlierResult,
        analysis_type: 'comprehensive'
      });
      
      return response;
    } catch (error) {
      console.warn('AI analysis failed, using fallback analysis');
      return generateFallbackAnalysis(outlierResult);
    }
  };

  const generateFallbackAnalysis = (outlierResult: any) => {
    const riskFactors = [];
    const strengths = [];
    const recommendations = [];
    
    // Analyze metrics to generate insights
    if (outlierResult.metrics.performance_score < 3.0) {
      riskFactors.push('Low performance score indicating potential productivity issues');
      recommendations.push('Provide targeted performance coaching and skill development');
    } else if (outlierResult.metrics.performance_score > 4.5) {
      strengths.push('Exceptional performance indicating high potential');
      recommendations.push('Consider for leadership development and mentoring opportunities');
    }
    
    if (outlierResult.metrics.engagement_score < 3.0) {
      riskFactors.push('Low engagement score suggesting disengagement risk');
      recommendations.push('Schedule one-on-one meetings to understand concerns and improve engagement');
    } else if (outlierResult.metrics.engagement_score > 4.5) {
      strengths.push('High engagement indicating strong organizational commitment');
      recommendations.push('Leverage as change champion and culture ambassador');
    }
    
    if (outlierResult.metrics.satisfaction_score < 3.0) {
      riskFactors.push('Low satisfaction score indicating potential turnover risk');
      recommendations.push('Conduct detailed exit interview preparation and retention strategies');
    }
    
    return {
      risk_factors: riskFactors,
      strengths: strengths,
      recommendations: recommendations,
      intervention_priority: riskFactors.length > 2 ? 9 : riskFactors.length > 0 ? 6 : 3,
      predicted_outcome: riskFactors.length > 2 ? 'High risk of turnover without intervention' : 
                        strengths.length > 1 ? 'High potential for advancement and leadership' : 
                        'Stable performance with room for improvement'
    };
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'positive': return 'bg-green-100 text-green-800';
      case 'negative': return 'bg-red-100 text-red-800';
      case 'neutral': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredOutliers = outliers.filter(outlier => {
    const matchesDepartment = !selectedDepartment || selectedDepartment === 'All' || outlier.department === selectedDepartment;
    const matchesSeverity = !selectedSeverity || selectedSeverity === 'All' || outlier.outlier_severity === selectedSeverity;
    const matchesType = !selectedType || selectedType === 'All' || outlier.outlier_type === selectedType;
    const matchesConfidence = outlier.confidence_score >= confidenceThreshold;
    
    return matchesDepartment && matchesSeverity && matchesType && matchesConfidence;
  });

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
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🔍 Outlier Detection System</h1>
          <p className="text-gray-600">AI-powered employee outlier detection with comprehensive analysis and recommendations</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={detectOutliers}
            disabled={analyzing}
            className="bg-gradient-to-r from-purple-500 to-pink-600 text-white px-6 py-3 rounded-lg hover:from-purple-600 hover:to-pink-700 transition-all flex items-center shadow-lg disabled:opacity-50"
          >
            {analyzing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Analyzing...
              </>
            ) : (
              <>
                <span className="mr-2">🤖</span>
                Run Detection
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-6 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <span className="text-2xl">👥</span>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-600">Total Outliers</h3>
                <p className="text-2xl font-bold text-gray-900">{summary.total_outliers}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <span className="text-2xl">⭐</span>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-600">High Performers</h3>
                <p className="text-2xl font-bold text-green-600">{summary.positive_outliers}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-red-100 rounded-lg">
                <span className="text-2xl">⚠️</span>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-600">At Risk</h3>
                <p className="text-2xl font-bold text-red-600">{summary.negative_outliers}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-orange-100 rounded-lg">
                <span className="text-2xl">🚨</span>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-600">Critical</h3>
                <p className="text-2xl font-bold text-orange-600">{summary.critical_outliers}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <span className="text-2xl">🏢</span>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-600">Departments</h3>
                <p className="text-2xl font-bold text-purple-600">{summary.departments_affected}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-indigo-100 rounded-lg">
                <span className="text-2xl">🎯</span>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-600">Confidence</h3>
                <p className="text-2xl font-bold text-indigo-600">{Math.round(summary.average_confidence * 100)}%</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Detection Configuration */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Detection Configuration</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Detection Method</label>
            <select
              value={detectionMethod}
              onChange={(e) => setDetectionMethod(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              {detectionMethods.map(method => (
                <option key={method.value} value={method.value}>
                  {method.label}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">
              {detectionMethods.find(m => m.value === detectionMethod)?.description}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Sensitivity Threshold</label>
            <input
              type="range"
              min="1.0"
              max="3.0"
              step="0.1"
              value={customThreshold}
              onChange={(e) => setCustomThreshold(parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Sensitive ({customThreshold})</span>
              <span>Conservative</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Confidence Threshold</label>
            <input
              type="range"
              min="0.5"
              max="1.0"
              step="0.05"
              value={confidenceThreshold}
              onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Low ({Math.round(confidenceThreshold * 100)}%)</span>
              <span>High</span>
            </div>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">Metrics to Analyze</label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {availableMetrics.map(metric => (
              <label key={metric.value} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                <input
                  type="checkbox"
                  checked={metrics.includes(metric.value)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setMetrics(prev => [...prev, metric.value]);
                    } else {
                      setMetrics(prev => prev.filter(m => m !== metric.value));
                    }
                  }}
                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <div>
                  <p className="text-sm font-medium text-gray-900">{metric.label}</p>
                  <p className="text-xs text-gray-500">{metric.category}</p>
                </div>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Department</label>
            <select
              value={selectedDepartment}
              onChange={(e) => setSelectedDepartment(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              {departments.map(dept => (
                <option key={dept} value={dept === 'All' ? '' : dept}>{dept}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Severity Level</label>
            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              {severityLevels.map(level => (
                <option key={level} value={level === 'All' ? '' : level}>{level}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Outlier Type</label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              {outlierTypes.map(type => (
                <option key={type} value={type === 'All' ? '' : type}>{type}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={() => {
                setSelectedDepartment('');
                setSelectedSeverity('');
                setSelectedType('');
                setConfidenceThreshold(0.7);
              }}
              className="w-full px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Outlier Results */}
      <div className="space-y-6">
        {filteredOutliers.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
              <span className="text-4xl">🔍</span>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No outliers detected</h3>
            <p className="text-gray-600 mb-4">
              {outliers.length === 0 
                ? "Run the detection system to identify employee outliers using AI-powered analysis."
                : "No outliers match your current filter criteria. Try adjusting the filters above."
              }
            </p>
            {outliers.length === 0 && (
              <button 
                onClick={detectOutliers}
                disabled={analyzing}
                className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
              >
                {analyzing ? 'Analyzing...' : 'Start Detection'}
              </button>
            )}
          </div>
        ) : (
          filteredOutliers.map((outlier) => (
            <div key={outlier.employee_id} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-xl font-semibold text-gray-900">{outlier.employee_name}</h3>
                    <span className={`px-3 py-1 text-sm font-medium rounded-full ${getTypeColor(outlier.outlier_type)}`}>
                      {outlier.outlier_type.toUpperCase()}
                    </span>
                    <span className={`px-3 py-1 text-sm font-medium rounded-full border ${getSeverityColor(outlier.outlier_severity)}`}>
                      {outlier.outlier_severity.toUpperCase()}
                    </span>
                    <span className="px-3 py-1 text-sm font-medium rounded-full bg-indigo-100 text-indigo-800">
                      {Math.round(outlier.confidence_score * 100)}% Confidence
                    </span>
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-gray-600 mb-4">
                    <span>🏢 {outlier.department}</span>
                    <span>💼 {outlier.position}</span>
                    <span>🔬 {outlier.detection_method}</span>
                    <span>📅 {new Date(outlier.detected_at).toLocaleDateString()}</span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Priority</p>
                    <p className="text-2xl font-bold text-red-600">{outlier.ai_analysis.intervention_priority}/10</p>
                  </div>
                </div>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <h4 className="text-sm font-medium text-gray-600">Performance</h4>
                  <p className="text-2xl font-bold text-gray-900">{outlier.metrics.performance_score.toFixed(1)}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <h4 className="text-sm font-medium text-gray-600">Engagement</h4>
                  <p className="text-2xl font-bold text-gray-900">{outlier.metrics.engagement_score.toFixed(1)}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <h4 className="text-sm font-medium text-gray-600">Satisfaction</h4>
                  <p className="text-2xl font-bold text-gray-900">{outlier.metrics.satisfaction_score.toFixed(1)}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <h4 className="text-sm font-medium text-gray-600">Deviation</h4>
                  <p className="text-2xl font-bold text-orange-600">{outlier.metrics.deviation_score.toFixed(2)}</p>
                </div>
              </div>

              {/* AI Analysis */}
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6 mb-4">
                <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <span className="mr-2">🤖</span>
                  AI Analysis & Insights
                </h4>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {outlier.ai_analysis.risk_factors.length > 0 && (
                    <div>
                      <h5 className="font-medium text-red-700 mb-2">🚨 Risk Factors</h5>
                      <ul className="space-y-1">
                        {outlier.ai_analysis.risk_factors.map((factor, index) => (
                          <li key={index} className="text-sm text-red-600">• {factor}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {outlier.ai_analysis.strengths.length > 0 && (
                    <div>
                      <h5 className="font-medium text-green-700 mb-2">💪 Strengths</h5>
                      <ul className="space-y-1">
                        {outlier.ai_analysis.strengths.map((strength, index) => (
                          <li key={index} className="text-sm text-green-600">• {strength}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  <div>
                    <h5 className="font-medium text-blue-700 mb-2">💡 Recommendations</h5>
                    <ul className="space-y-1">
                      {outlier.ai_analysis.recommendations.map((recommendation, index) => (
                        <li key={index} className="text-sm text-blue-600">• {recommendation}</li>
                      ))}
                    </ul>
                  </div>
                </div>
                
                <div className="mt-4 p-3 bg-white rounded-lg">
                  <h5 className="font-medium text-gray-700 mb-1">🔮 Predicted Outcome</h5>
                  <p className="text-sm text-gray-600">{outlier.ai_analysis.predicted_outcome}</p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3">
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  📋 Create Action Plan
                </button>
                <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                  👥 Add to Focus Group
                </button>
                <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                  📊 View Full Profile
                </button>
                <button className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
                  📞 Schedule Meeting
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
} 