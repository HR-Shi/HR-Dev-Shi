import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../api';

interface KPIWidget {
  id: string;
  title: string;
  value: number;
  target: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  trendValue: number;
  category: string;
  status: 'excellent' | 'good' | 'warning' | 'critical';
  lastUpdated: string;
}

interface AlertItem {
  id: string;
  type: 'warning' | 'critical' | 'info';
  title: string;
  message: string;
  timestamp: string;
  category: string;
}

interface TeamHealth {
  department: string;
  overallScore: number;
  engagement: number;
  performance: number;
  retention: number;
  trend: 'improving' | 'stable' | 'declining';
}

export function RealTimeDashboard() {
  const [kpiWidgets, setKpiWidgets] = useState<KPIWidget[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [teamHealth, setTeamHealth] = useState<TeamHealth[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedTimeframe, setSelectedTimeframe] = useState('7d');
  const [autoRefresh, setAutoRefresh] = useState(true);

  const timeframes = [
    { value: '24h', label: '24 Hours' },
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' }
  ];

  useEffect(() => {
    fetchDashboardData();
  }, [selectedTimeframe]);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // Mock data - replace with real API calls
      setKpiWidgets(generateMockKPIWidgets());
      setAlerts(generateMockAlerts());
      setTeamHealth(generateMockTeamHealth());
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateMockKPIWidgets = (): KPIWidget[] => {
    return [
      {
        id: '1',
        title: 'Employee Engagement',
        value: 78,
        target: 80,
        unit: '%',
        trend: 'up',
        trendValue: 2.3,
        category: 'engagement',
        status: 'good',
        lastUpdated: new Date().toISOString()
      },
      {
        id: '2',
        title: 'Turnover Rate',
        value: 8.2,
        target: 10,
        unit: '%',
        trend: 'down',
        trendValue: -1.1,
        category: 'retention',
        status: 'excellent',
        lastUpdated: new Date().toISOString()
      },
      {
        id: '3',
        title: 'Performance Score',
        value: 4.2,
        target: 4.0,
        unit: '/5',
        trend: 'up',
        trendValue: 0.15,
        category: 'performance',
        status: 'excellent',
        lastUpdated: new Date().toISOString()
      },
      {
        id: '4',
        title: 'Training Completion',
        value: 85,
        target: 90,
        unit: '%',
        trend: 'stable',
        trendValue: 0,
        category: 'development',
        status: 'warning',
        lastUpdated: new Date().toISOString()
      },
      {
        id: '5',
        title: 'Absenteeism Rate',
        value: 3.2,
        target: 3.0,
        unit: '%',
        trend: 'up',
        trendValue: 0.4,
        category: 'wellness',
        status: 'warning',
        lastUpdated: new Date().toISOString()
      },
      {
        id: '6',
        title: 'Diversity Index',
        value: 72,
        target: 75,
        unit: '%',
        trend: 'up',
        trendValue: 1.8,
        category: 'diversity',
        status: 'good',
        lastUpdated: new Date().toISOString()
      }
    ];
  };

  const generateMockAlerts = (): AlertItem[] => {
    return [
      {
        id: '1',
        type: 'critical',
        title: 'High Turnover Alert',
        message: 'Engineering department showing 15% turnover rate - above threshold',
        timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
        category: 'retention'
      },
      {
        id: '2',
        type: 'warning',
        title: 'Low Survey Response',
        message: 'Q4 engagement survey response rate below 60%',
        timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
        category: 'engagement'
      },
      {
        id: '3',
        type: 'info',
        title: 'Training Milestone',
        message: 'Leadership development program completed by 25 employees',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
        category: 'development'
      }
    ];
  };

  const generateMockTeamHealth = (): TeamHealth[] => {
    return [
      { department: 'Engineering', overallScore: 78, engagement: 82, performance: 85, retention: 68, trend: 'improving' },
      { department: 'Sales', overallScore: 85, engagement: 88, performance: 90, retention: 78, trend: 'stable' },
      { department: 'Marketing', overallScore: 72, engagement: 75, performance: 78, retention: 85, trend: 'declining' },
      { department: 'HR', overallScore: 90, engagement: 92, performance: 88, retention: 90, trend: 'improving' },
      { department: 'Finance', overallScore: 81, engagement: 79, performance: 85, retention: 79, trend: 'stable' }
    ];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'text-green-600 bg-green-50 border-green-200';
      case 'good': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'critical': return 'bg-red-100 border-red-400 text-red-800';
      case 'warning': return 'bg-yellow-100 border-yellow-400 text-yellow-800';
      case 'info': return 'bg-blue-100 border-blue-400 text-blue-800';
      default: return 'bg-gray-100 border-gray-400 text-gray-800';
    }
  };

  const getTrendIcon = (trend: string, trendValue: number) => {
    if (trend === 'up') return <span className="text-green-500">📈 +{trendValue}%</span>;
    if (trend === 'down') return <span className="text-red-500">📉 {trendValue}%</span>;
    return <span className="text-gray-500">➡️ {trendValue}%</span>;
  };

  const getProgressPercentage = (value: number, target: number) => {
    return Math.min((value / target) * 100, 100);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">📊 Real-Time HR Dashboard</h1>
          <p className="text-gray-600">Live monitoring of key HR metrics and organizational health</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Timeframe:</label>
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm"
            >
              {timeframes.map(tf => (
                <option key={tf.value} value={tf.value}>{tf.label}</option>
              ))}
            </select>
          </div>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              autoRefresh 
                ? 'bg-green-100 text-green-800 border border-green-300' 
                : 'bg-gray-100 text-gray-800 border border-gray-300'
            }`}
          >
            {autoRefresh ? '🔄 Auto-refresh ON' : '⏸️ Auto-refresh OFF'}
          </button>
          <button
            onClick={fetchDashboardData}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            🔄 Refresh Now
          </button>
        </div>
      </div>

      {/* Live Alerts */}
      {alerts.length > 0 && (
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">🚨 Live Alerts</h2>
          <div className="space-y-3">
            {alerts.slice(0, 3).map(alert => (
              <div key={alert.id} className={`border-l-4 p-4 rounded-r-lg ${getAlertColor(alert.type)}`}>
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold">{alert.title}</h3>
                    <p className="text-sm mt-1">{alert.message}</p>
                  </div>
                  <span className="text-xs opacity-75">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* KPI Widgets Grid */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">📈 Key Performance Indicators</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {kpiWidgets.map(kpi => (
            <div key={kpi.id} className={`bg-white rounded-lg shadow border-l-4 p-6 ${getStatusColor(kpi.status).split(' ').slice(2).join(' ')}`}>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-600">{kpi.title}</h3>
                  <div className="flex items-baseline mt-1">
                    <p className={`text-2xl font-bold ${getStatusColor(kpi.status).split(' ')[0]}`}>
                      {kpi.value}{kpi.unit}
                    </p>
                    <span className="ml-2 text-sm text-gray-500">/ {kpi.target}{kpi.unit}</span>
                  </div>
                </div>
                <div className="text-right">
                  {getTrendIcon(kpi.trend, kpi.trendValue)}
                </div>
              </div>
              
              {/* Progress Bar */}
              <div className="mb-3">
                <div className="flex justify-between text-xs text-gray-600 mb-1">
                  <span>Progress to Target</span>
                  <span>{Math.round(getProgressPercentage(kpi.value, kpi.target))}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      kpi.status === 'excellent' ? 'bg-green-500' :
                      kpi.status === 'good' ? 'bg-blue-500' :
                      kpi.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${getProgressPercentage(kpi.value, kpi.target)}%` }}
                  />
                </div>
              </div>
              
              <div className="flex justify-between items-center text-xs text-gray-500">
                <span className={`px-2 py-1 rounded-full ${getStatusColor(kpi.status)}`}>
                  {kpi.status.toUpperCase()}
                </span>
                <span>Updated: {new Date(kpi.lastUpdated).toLocaleTimeString()}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Team Health Overview */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">🏥 Team Health Overview</h2>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="space-y-6">
            {teamHealth.map(team => (
              <div key={team.department} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-semibold text-gray-900">{team.department}</h3>
                  <div className="flex items-center space-x-2">
                    <span className={`px-3 py-1 rounded-full text-sm ${
                      team.trend === 'improving' ? 'bg-green-100 text-green-800' :
                      team.trend === 'stable' ? 'bg-blue-100 text-blue-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {team.trend === 'improving' ? '↗️' : team.trend === 'stable' ? '➡️' : '↘️'} {team.trend}
                    </span>
                    <span className="text-2xl font-bold text-gray-900">{team.overallScore}</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Engagement</p>
                    <div className="mt-1">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${team.engagement}%` }}
                        />
                      </div>
                      <p className="text-sm font-semibold mt-1">{team.engagement}%</p>
                    </div>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Performance</p>
                    <div className="mt-1">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${team.performance}%` }}
                        />
                      </div>
                      <p className="text-sm font-semibold mt-1">{team.performance}%</p>
                    </div>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Retention</p>
                    <div className="mt-1">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-purple-500 h-2 rounded-full"
                          style={{ width: `${team.retention}%` }}
                        />
                      </div>
                      <p className="text-sm font-semibold mt-1">{team.retention}%</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">⚡ Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
            <div className="text-2xl mb-2">📋</div>
            <h3 className="font-semibold text-gray-900">Create Survey</h3>
            <p className="text-sm text-gray-600">Launch new engagement survey</p>
          </button>
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
            <div className="text-2xl mb-2">🎯</div>
            <h3 className="font-semibold text-gray-900">Set KPI Target</h3>
            <p className="text-sm text-gray-600">Update performance targets</p>
          </button>
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
            <div className="text-2xl mb-2">🚨</div>
            <h3 className="font-semibold text-gray-900">Create Alert</h3>
            <p className="text-sm text-gray-600">Set up monitoring alerts</p>
          </button>
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
            <div className="text-2xl mb-2">📊</div>
            <h3 className="font-semibold text-gray-900">Generate Report</h3>
            <p className="text-sm text-gray-600">Export dashboard data</p>
          </button>
        </div>
      </div>
    </div>
  );
} 