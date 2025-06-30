import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { EngagementChart } from '../components/charts/EngagementChart';
import { KPIGauge } from '../components/charts/KPIGauge';
import { dashboardAPI } from '../api';
import { DashboardOverview, KPI, Outlier } from '../types';
import { Users, TrendingUp, AlertTriangle, CheckCircle, Activity, Target } from 'lucide-react';

export function Overview() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [outliers, setOutliers] = useState<Outlier[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [overviewData, kpisData, outliersData] = await Promise.all([
          dashboardAPI.getOverview(),
          dashboardAPI.getKPIs(),
          dashboardAPI.getOutliers(),
        ]);
        setOverview(overviewData);
        setKpis(kpisData);
        setOutliers(outliersData);
      } catch (error) {
        console.error('Error fetching overview data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!overview) return <div>Error loading data</div>;

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">HR Dashboard Overview</h1>
        <p className="text-gray-600">Real-time insights and key performance indicators</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg mr-4">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Employees</p>
              <p className="text-2xl font-bold text-gray-900">{overview.total_employees}</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg mr-4">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Avg Engagement</p>
              <p className="text-2xl font-bold text-gray-900">{overview.avg_engagement}%</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-orange-100 rounded-lg mr-4">
              <AlertTriangle className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">High Concern</p>
              <p className="text-2xl font-bold text-gray-900">{overview.high_concern}</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-teal-100 rounded-lg mr-4">
              <Activity className="w-6 h-6 text-teal-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Active Surveys</p>
              <p className="text-2xl font-bold text-gray-900">{overview.active_surveys}</p>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Engagement Trend */}
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Engagement Trend</h3>
          <EngagementChart data={overview.engagement_trend} />
        </Card>

        {/* Employee Status Distribution */}
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Employee Status</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-green-500 rounded mr-3"></div>
                <span className="text-gray-700">Good Status</span>
              </div>
              <div className="flex items-center">
                <span className="text-lg font-semibold mr-2">{overview.good_status}</span>
                <Badge variant="success">
                  {Math.round((overview.good_status / overview.total_employees) * 100)}%
                </Badge>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-yellow-500 rounded mr-3"></div>
                <span className="text-gray-700">Mid Concern</span>
              </div>
              <div className="flex items-center">
                <span className="text-lg font-semibold mr-2">{overview.mid_concern}</span>
                <Badge variant="warning">
                  {Math.round((overview.mid_concern / overview.total_employees) * 100)}%
                </Badge>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-red-500 rounded mr-3"></div>
                <span className="text-gray-700">High Concern</span>
              </div>
              <div className="flex items-center">
                <span className="text-lg font-semibold mr-2">{overview.high_concern}</span>
                <Badge variant="error">
                  {Math.round((overview.high_concern / overview.total_employees) * 100)}%
                </Badge>
              </div>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* KPI Snapshot */}
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-6">KPI Snapshot</h3>
          <div className="grid grid-cols-2 gap-6">
            {kpis.slice(0, 4).map((kpi) => (
              <KPIGauge
                key={kpi.id}
                value={kpi.current_value}
                target={kpi.target_value}
                label={kpi.name}
                unit={kpi.name.includes('Rate') ? '%' : ''}
              />
            ))}
          </div>
        </Card>

        {/* Outlier Alerts */}
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Outlier Alerts</h3>
          <div className="space-y-3">
            {outliers.slice(0, 5).map((outlier) => (
              <div key={outlier.id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{outlier.name}</p>
                  <p className="text-sm text-gray-600">{outlier.department}</p>
                </div>
                <div className="text-right">
                  <Badge variant="error">{outlier.engagement_score}%</Badge>
                  <p className="text-xs text-gray-500 mt-1">
                    {outlier.risk_factors.join(', ')}
                  </p>
                </div>
              </div>
            ))}
            {outliers.length === 0 && (
              <div className="text-center py-6 text-gray-500">
                <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
                <p>No outliers detected</p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}