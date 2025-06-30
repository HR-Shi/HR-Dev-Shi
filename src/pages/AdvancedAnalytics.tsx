import React, { useState } from 'react';

interface DepartmentMetrics {
  department: string;
  engagement: number;
  performance: number;
  retention: number;
  satisfaction: number;
  growth: number;
  wellness: number;
  employeeCount: number;
  trend: 'up' | 'down' | 'stable';
}

interface TrendData {
  month: string;
  engagement: number;
  turnover: number;
  performance: number;
  satisfaction: number;
}

interface PredictiveInsight {
  category: string;
  risk: 'low' | 'medium' | 'high';
  prediction: string;
  confidence: number;
  recommendation: string;
  timeframe: string;
}

export function AdvancedAnalytics() {
  const [selectedDepartment, setSelectedDepartment] = useState('All');
  const [timeRange, setTimeRange] = useState('12m');
  const [selectedMetric, setSelectedMetric] = useState('engagement');

  const departmentData: DepartmentMetrics[] = [
    { department: 'Engineering', engagement: 78, performance: 85, retention: 72, satisfaction: 80, growth: 88, wellness: 75, employeeCount: 45, trend: 'up' },
    { department: 'Sales', engagement: 85, performance: 92, retention: 68, satisfaction: 86, growth: 90, wellness: 82, employeeCount: 32, trend: 'up' },
    { department: 'Marketing', engagement: 72, performance: 78, retention: 85, satisfaction: 74, growth: 85, wellness: 79, employeeCount: 18, trend: 'down' },
    { department: 'HR', engagement: 90, performance: 88, retention: 95, satisfaction: 92, growth: 85, wellness: 88, employeeCount: 12, trend: 'up' },
    { department: 'Finance', engagement: 75, performance: 82, retention: 88, satisfaction: 77, growth: 75, wellness: 73, employeeCount: 15, trend: 'stable' },
    { department: 'Operations', engagement: 68, performance: 75, retention: 80, satisfaction: 70, growth: 72, wellness: 68, employeeCount: 28, trend: 'down' },
    { department: 'Legal', engagement: 82, performance: 86, retention: 90, satisfaction: 84, growth: 78, wellness: 85, employeeCount: 8, trend: 'stable' },
    { department: 'IT', engagement: 80, performance: 88, retention: 75, satisfaction: 82, growth: 85, wellness: 78, employeeCount: 22, trend: 'up' }
  ];

  const trendData: TrendData[] = [
    { month: 'Jan', engagement: 72, turnover: 12, performance: 78, satisfaction: 75 },
    { month: 'Feb', engagement: 74, turnover: 11, performance: 80, satisfaction: 77 },
    { month: 'Mar', engagement: 76, turnover: 10, performance: 82, satisfaction: 79 },
    { month: 'Apr', engagement: 73, turnover: 13, performance: 81, satisfaction: 76 },
    { month: 'May', engagement: 78, turnover: 9, performance: 84, satisfaction: 81 },
    { month: 'Jun', engagement: 80, turnover: 8, performance: 86, satisfaction: 83 },
    { month: 'Jul', engagement: 79, turnover: 9, performance: 85, satisfaction: 82 },
    { month: 'Aug', engagement: 81, turnover: 7, performance: 87, satisfaction: 84 },
    { month: 'Sep', engagement: 83, turnover: 6, performance: 88, satisfaction: 86 },
    { month: 'Oct', engagement: 85, turnover: 5, performance: 90, satisfaction: 87 },
    { month: 'Nov', engagement: 82, turnover: 8, performance: 89, satisfaction: 85 },
    { month: 'Dec', engagement: 84, turnover: 7, performance: 91, satisfaction: 88 }
  ];

  const predictiveInsights: PredictiveInsight[] = [
    {
      category: 'Turnover Risk',
      risk: 'high',
      prediction: 'Engineering department likely to see 18% turnover in Q2',
      confidence: 87,
      recommendation: 'Implement retention program and conduct stay interviews',
      timeframe: 'Next 3 months'
    },
    {
      category: 'Performance Decline',
      risk: 'medium',
      prediction: 'Marketing team performance trending downward',
      confidence: 72,
      recommendation: 'Provide additional training and management support',
      timeframe: 'Next 6 weeks'
    },
    {
      category: 'Engagement Growth',
      risk: 'low',
      prediction: 'Sales team engagement will continue improving',
      confidence: 91,
      recommendation: 'Leverage sales team practices across other departments',
      timeframe: 'Ongoing'
    },
    {
      category: 'Wellness Alert',
      risk: 'medium',
      prediction: 'Operations team showing signs of burnout',
      confidence: 78,
      recommendation: 'Implement wellness programs and workload assessment',
      timeframe: 'Next 4 weeks'
    }
  ];

  const getHeatmapColor = (value: number) => {
    if (value >= 85) return 'bg-green-500';
    if (value >= 75) return 'bg-green-400';
    if (value >= 65) return 'bg-yellow-400';
    if (value >= 55) return 'bg-orange-400';
    return 'bg-red-400';
  };

  const getTextColor = (value: number) => {
    return value >= 65 ? 'text-white' : 'text-gray-900';
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const metrics = [
    { key: 'engagement', label: 'Engagement', icon: '💝' },
    { key: 'performance', label: 'Performance', icon: '📊' },
    { key: 'retention', label: 'Retention', icon: '🔄' },
    { key: 'satisfaction', label: 'Satisfaction', icon: '😊' },
    { key: 'growth', label: 'Growth', icon: '📈' },
    { key: 'wellness', label: 'Wellness', icon: '💪' }
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">📊 Advanced Analytics</h1>
          <p className="text-gray-600">Deep insights with predictive analytics and department comparisons</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedDepartment}
            onChange={(e) => setSelectedDepartment(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm"
          >
            <option value="All">All Departments</option>
            {departmentData.map(dept => (
              <option key={dept.department} value={dept.department}>{dept.department}</option>
            ))}
          </select>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm"
          >
            <option value="3m">Last 3 Months</option>
            <option value="6m">Last 6 Months</option>
            <option value="12m">Last 12 Months</option>
            <option value="24m">Last 24 Months</option>
          </select>
        </div>
      </div>

      {/* Metric Selector */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Metric for Heatmap</h2>
        <div className="flex flex-wrap gap-2">
          {metrics.map(metric => (
            <button
              key={metric.key}
              onClick={() => setSelectedMetric(metric.key)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedMetric === metric.key
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {metric.icon} {metric.label}
            </button>
          ))}
        </div>
      </div>

      {/* Department Heatmap */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">🔥 Department Heatmap - {metrics.find(m => m.key === selectedMetric)?.label}</h2>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {departmentData.map(dept => {
              const value = dept[selectedMetric as keyof DepartmentMetrics] as number;
              return (
                <div key={dept.department} className="relative">
                  <div className={`${getHeatmapColor(value)} rounded-lg p-4 text-center transition-all duration-300 hover:scale-105`}>
                    <h3 className={`font-semibold ${getTextColor(value)}`}>{dept.department}</h3>
                    <p className={`text-2xl font-bold ${getTextColor(value)}`}>{value}%</p>
                    <p className={`text-sm ${getTextColor(value)} opacity-75`}>
                      {dept.employeeCount} employees
                    </p>
                    <div className={`absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      dept.trend === 'up' ? 'bg-green-500 text-white' :
                      dept.trend === 'down' ? 'bg-red-500 text-white' :
                      'bg-gray-500 text-white'
                    }`}>
                      {dept.trend === 'up' ? '↗' : dept.trend === 'down' ? '↘' : '→'}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          
          {/* Heatmap Legend */}
          <div className="mt-6 flex items-center justify-center space-x-4">
            <span className="text-sm text-gray-600">Scale:</span>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-red-400 rounded"></div>
              <span className="text-sm">0-55%</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-orange-400 rounded"></div>
              <span className="text-sm">55-65%</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-yellow-400 rounded"></div>
              <span className="text-sm">65-75%</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-400 rounded"></div>
              <span className="text-sm">75-85%</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-500 rounded"></div>
              <span className="text-sm">85%+</span>
            </div>
          </div>
        </div>
      </div>

      {/* Trend Analysis */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">📈 12-Month Trend Analysis</h2>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Engagement & Satisfaction Trends */}
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Engagement & Satisfaction</h3>
              <div className="space-y-2">
                {trendData.slice(-6).map((data, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 w-12">{data.month}</span>
                    <div className="flex-1 mx-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${data.engagement}%` }}
                          />
                        </div>
                        <span className="text-sm w-8">{data.engagement}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Performance & Turnover */}
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Performance & Turnover</h3>
              <div className="space-y-2">
                {trendData.slice(-6).map((data, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 w-12">{data.month}</span>
                    <div className="flex-1 mx-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${data.performance}%` }}
                          />
                        </div>
                        <span className="text-sm w-8">{data.performance}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Predictive Insights */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">🔮 AI Predictive Insights</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {predictiveInsights.map((insight, index) => (
            <div key={index} className="bg-white rounded-lg shadow border p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="font-semibold text-gray-900">{insight.category}</h3>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(insight.risk)}`}>
                  {insight.risk.toUpperCase()} RISK
                </span>
              </div>
              
              <p className="text-gray-700 mb-4">{insight.prediction}</p>
              
              <div className="mb-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Confidence Level</span>
                  <span className="text-sm font-semibold">{insight.confidence}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${insight.confidence}%` }}
                  />
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                <h4 className="font-medium text-gray-900 mb-2">💡 Recommendation:</h4>
                <p className="text-sm text-gray-700">{insight.recommendation}</p>
              </div>
              
              <div className="flex justify-between items-center text-sm text-gray-600">
                <span>⏰ {insight.timeframe}</span>
                <button className="text-blue-600 hover:text-blue-800 font-medium">View Details →</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Comparative Analysis */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">⚖️ Cross-Department Comparison</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-900">Department</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-900">Employees</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-900">Engagement</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-900">Performance</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-900">Retention</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-900">Satisfaction</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-900">Trend</th>
              </tr>
            </thead>
            <tbody>
              {departmentData.map((dept, index) => (
                <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 font-medium text-gray-900">{dept.department}</td>
                  <td className="py-3 px-4 text-center text-gray-600">{dept.employeeCount}</td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-2 py-1 rounded-full text-sm font-medium ${
                      dept.engagement >= 80 ? 'bg-green-100 text-green-800' :
                      dept.engagement >= 70 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {dept.engagement}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-2 py-1 rounded-full text-sm font-medium ${
                      dept.performance >= 80 ? 'bg-green-100 text-green-800' :
                      dept.performance >= 70 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {dept.performance}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-2 py-1 rounded-full text-sm font-medium ${
                      dept.retention >= 80 ? 'bg-green-100 text-green-800' :
                      dept.retention >= 70 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {dept.retention}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-2 py-1 rounded-full text-sm font-medium ${
                      dept.satisfaction >= 80 ? 'bg-green-100 text-green-800' :
                      dept.satisfaction >= 70 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {dept.satisfaction}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`text-lg ${
                      dept.trend === 'up' ? 'text-green-500' :
                      dept.trend === 'down' ? 'text-red-500' :
                      'text-gray-500'
                    }`}>
                      {dept.trend === 'up' ? '📈' : dept.trend === 'down' ? '📉' : '➡️'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
} 