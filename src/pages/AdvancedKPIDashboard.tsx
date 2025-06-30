import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  TrendingUp, 
  Brain, 
  Users, 
  Zap, 
  Target, 
  BarChart3, 
  LineChart, 
  PieChart, 
  Calendar,
  RefreshCw,
  Download,
  Filter,
  Info,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart as RechartsBarChart, Bar, PieChart as RechartsPieChart, Cell, Pie, RadialBarChart, RadialBar } from 'recharts';
import api from '@/api';

interface KPIDefinition {
  kpi_code: string;
  name: string;
  description: string;
  formula_expression: string;
  parameter_weights: Record<string, number>;
  target_value?: number;
  calculation_frequency: string;
}

interface KPIResult {
  employee_id: string;
  employee_name: string;
  kpi_code: string;
  kpi_name: string;
  calculated_value: number;
  component_scores: Record<string, number>;
  calculation_date: string;
  period_start: string;
  period_end: string;
  confidence_score: number;
}

interface Employee {
  id: string;
  name: string;
  email: string;
  position: string;
  department_id: string;
}

interface Department {
  id: string;
  name: string;
}

const AdvancedKPIDashboard: React.FC = () => {
  const [kpiDefinitions, setKpiDefinitions] = useState<KPIDefinition[]>([]);
  const [kpiResults, setKpiResults] = useState<KPIResult[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [selectedDepartment, setSelectedDepartment] = useState<string>('all');
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>('30');
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const kpiIcons = {
    'FRLP': Brain,
    'IV': Zap,
    'CHI': Users
  };

  const kpiColors = {
    'FRLP': '#3B82F6', // Blue
    'IV': '#F59E0B',   // Orange
    'CHI': '#10B981'   // Green
  };

  useEffect(() => {
    loadData();
  }, [selectedDepartment, selectedTimeRange]);

  const loadData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadKPIDefinitions(),
        loadKPIResults(),
        loadEmployees(),
        loadDepartments()
      ]);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadKPIDefinitions = async () => {
    try {
      const response = await api.get('/parameters/kpis/definitions');
      setKpiDefinitions(response.data);
    } catch (error) {
      console.error('Failed to load KPI definitions:', error);
    }
  };

  const loadKPIResults = async () => {
    try {
      // For now, get all results and filter client-side
      // In production, you'd want to filter server-side
      const response = await api.get('/parameters/kpis/results', {
        params: {
          department: selectedDepartment !== 'all' ? selectedDepartment : undefined,
          days: selectedTimeRange
        }
      });
      setKpiResults(response.data || []);
    } catch (error) {
      console.error('Failed to load KPI results:', error);
    }
  };

  const loadEmployees = async () => {
    try {
      const response = await api.get('/employees');
      setEmployees(response.data);
    } catch (error) {
      console.error('Failed to load employees:', error);
    }
  };

  const loadDepartments = async () => {
    try {
      const response = await api.get('/departments');
      setDepartments(response.data);
    } catch (error) {
      console.error('Failed to load departments:', error);
    }
  };

  const recalculateKPIs = async () => {
    try {
      setLoading(true);
      await api.post('/parameters/kpis/calculate/bulk');
      await loadKPIResults();
    } catch (error) {
      console.error('Failed to recalculate KPIs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getKPIStats = (kpiCode: string) => {
    const results = kpiResults.filter(r => r.kpi_code === kpiCode);
    if (results.length === 0) return null;

    const values = results.map(r => r.calculated_value);
    const average = values.reduce((sum, val) => sum + val, 0) / values.length;
    const max = Math.max(...values);
    const min = Math.min(...values);
    const median = values.sort((a, b) => a - b)[Math.floor(values.length / 2)];

    return { average, max, min, median, count: results.length };
  };

  const getKPITrend = (kpiCode: string) => {
    const results = kpiResults
      .filter(r => r.kpi_code === kpiCode)
      .sort((a, b) => new Date(a.calculation_date).getTime() - new Date(b.calculation_date).getTime());

    return results.map(r => ({
      date: new Date(r.calculation_date).toLocaleDateString(),
      value: r.calculated_value,
      employee: r.employee_name
    }));
  };

  const getKPIDistribution = (kpiCode: string) => {
    const results = kpiResults.filter(r => r.kpi_code === kpiCode);
    const ranges = [
      { name: 'Excellent (4.5-5.0)', min: 4.5, max: 5.0, color: '#10B981' },
      { name: 'Good (3.5-4.5)', min: 3.5, max: 4.5, color: '#3B82F6' },
      { name: 'Average (2.5-3.5)', min: 2.5, max: 3.5, color: '#F59E0B' },
      { name: 'Below Average (1.5-2.5)', min: 1.5, max: 2.5, color: '#EF4444' },
      { name: 'Poor (1.0-1.5)', min: 1.0, max: 1.5, color: '#991B1B' }
    ];

    return ranges.map(range => ({
      name: range.name,
      count: results.filter(r => r.calculated_value >= range.min && r.calculated_value < range.max).length,
      color: range.color
    }));
  };

  const getTopPerformers = (kpiCode: string, limit = 5) => {
    return kpiResults
      .filter(r => r.kpi_code === kpiCode)
      .sort((a, b) => b.calculated_value - a.calculated_value)
      .slice(0, limit);
  };

  const getBottomPerformers = (kpiCode: string, limit = 5) => {
    return kpiResults
      .filter(r => r.kpi_code === kpiCode)
      .sort((a, b) => a.calculated_value - b.calculated_value)
      .slice(0, limit);
  };

  const getScoreColor = (score: number) => {
    if (score >= 4.5) return 'text-green-600 bg-green-100';
    if (score >= 3.5) return 'text-blue-600 bg-blue-100';
    if (score >= 2.5) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 4.0) return CheckCircle;
    if (score >= 3.0) return AlertTriangle;
    return XCircle;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Advanced KPI Dashboard</h1>
            <p className="text-gray-600 mt-1">Future-Ready Leadership, Innovation Velocity & Collaborative Health metrics</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-sm text-gray-500">
              Last updated: {lastUpdated.toLocaleString()}
            </div>
            <Button onClick={recalculateKPIs} disabled={loading} variant="outline">
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Recalculate
            </Button>
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <Filter className="w-5 h-5 text-gray-500" />
              <Select value={selectedDepartment} onValueChange={setSelectedDepartment}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="All Departments" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Departments</SelectItem>
                  {departments.map(dept => (
                    <SelectItem key={dept.id} value={dept.id}>
                      {dept.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={selectedTimeRange} onValueChange={setSelectedTimeRange}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7">Last 7 days</SelectItem>
                  <SelectItem value="30">Last 30 days</SelectItem>
                  <SelectItem value="90">Last 90 days</SelectItem>
                  <SelectItem value="365">Last year</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* KPI Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {kpiDefinitions.map((kpi) => {
            const IconComponent = kpiIcons[kpi.kpi_code as keyof typeof kpiIcons];
            const stats = getKPIStats(kpi.kpi_code);
            const ScoreIcon = stats ? getScoreIcon(stats.average) : Info;
            
            return (
              <Card key={kpi.kpi_code} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div 
                        className="p-3 rounded-lg"
                        style={{ backgroundColor: kpiColors[kpi.kpi_code as keyof typeof kpiColors] + '20' }}
                      >
                        <IconComponent 
                          className="w-6 h-6" 
                          style={{ color: kpiColors[kpi.kpi_code as keyof typeof kpiColors] }}
                        />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{kpi.name}</CardTitle>
                        <Badge variant="secondary">{kpi.kpi_code}</Badge>
                      </div>
                    </div>
                    <ScoreIcon className="w-5 h-5 text-gray-400" />
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <p className="text-sm text-gray-600">{kpi.description}</p>
                  
                  {stats ? (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Average Score</span>
                        <Badge className={`${getScoreColor(stats.average)}`}>
                          {stats.average.toFixed(2)}/5.0
                        </Badge>
                      </div>
                      
                      <Progress value={stats.average * 20} className="h-2" />
                      
                      <div className="grid grid-cols-3 gap-4 text-sm text-gray-600">
                        <div className="text-center">
                          <div className="font-medium text-gray-900">{stats.max.toFixed(1)}</div>
                          <div>Best</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-gray-900">{stats.median.toFixed(1)}</div>
                          <div>Median</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-gray-900">{stats.min.toFixed(1)}</div>
                          <div>Lowest</div>
                        </div>
                      </div>
                      
                      <div className="text-center text-sm text-gray-500">
                        {stats.count} employees evaluated
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-gray-500 py-8">
                      <BarChart3 className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">No data available</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Detailed Analytics */}
        <Tabs defaultValue="trends" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="trends">Trends</TabsTrigger>
            <TabsTrigger value="distribution">Distribution</TabsTrigger>
            <TabsTrigger value="rankings">Rankings</TabsTrigger>
            <TabsTrigger value="components">Components</TabsTrigger>
          </TabsList>

          <TabsContent value="trends" className="space-y-6">
            {kpiDefinitions.map((kpi) => {
              const trendData = getKPITrend(kpi.kpi_code);
              const IconComponent = kpiIcons[kpi.kpi_code as keyof typeof kpiIcons];
              
              return (
                <Card key={kpi.kpi_code}>
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <IconComponent 
                        className="w-5 h-5" 
                        style={{ color: kpiColors[kpi.kpi_code as keyof typeof kpiColors] }}
                      />
                      <CardTitle>{kpi.name} - Trend Analysis</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {trendData.length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <RechartsLineChart data={trendData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis domain={[1, 5]} />
                          <Tooltip />
                          <Line 
                            type="monotone" 
                            dataKey="value" 
                            stroke={kpiColors[kpi.kpi_code as keyof typeof kpiColors]}
                            strokeWidth={2}
                            name="KPI Score"
                          />
                        </RechartsLineChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="text-center text-gray-500 py-8">
                        <LineChart className="w-8 h-8 mx-auto mb-2 opacity-50" />
                        <p>No trend data available</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </TabsContent>

          <TabsContent value="distribution" className="space-y-6">
            {kpiDefinitions.map((kpi) => {
              const distributionData = getKPIDistribution(kpi.kpi_code);
              const IconComponent = kpiIcons[kpi.kpi_code as keyof typeof kpiIcons];
              
              return (
                <Card key={kpi.kpi_code}>
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <IconComponent 
                        className="w-5 h-5" 
                        style={{ color: kpiColors[kpi.kpi_code as keyof typeof kpiColors] }}
                      />
                      <CardTitle>{kpi.name} - Score Distribution</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <ResponsiveContainer width="100%" height={300}>
                          <RechartsPieChart>
                            <Pie
                              data={distributionData}
                              cx="50%"
                              cy="50%"
                              labelLine={false}
                              label={({ name, count }) => `${name}: ${count}`}
                              outerRadius={80}
                              fill="#8884d8"
                              dataKey="count"
                            >
                              {distributionData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                              ))}
                            </Pie>
                            <Tooltip />
                          </RechartsPieChart>
                        </ResponsiveContainer>
                      </div>
                      
                      <div className="space-y-3">
                        {distributionData.map((range, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <div 
                                className="w-4 h-4 rounded-full"
                                style={{ backgroundColor: range.color }}
                              />
                              <span className="text-sm font-medium">{range.name}</span>
                            </div>
                            <Badge variant="outline">{range.count} employees</Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </TabsContent>

          <TabsContent value="rankings" className="space-y-6">
            {kpiDefinitions.map((kpi) => {
              const topPerformers = getTopPerformers(kpi.kpi_code);
              const bottomPerformers = getBottomPerformers(kpi.kpi_code);
              const IconComponent = kpiIcons[kpi.kpi_code as keyof typeof kpiIcons];
              
              return (
                <Card key={kpi.kpi_code}>
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <IconComponent 
                        className="w-5 h-5" 
                        style={{ color: kpiColors[kpi.kpi_code as keyof typeof kpiColors] }}
                      />
                      <CardTitle>{kpi.name} - Employee Rankings</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-semibold text-green-700 mb-3 flex items-center gap-2">
                          <TrendingUp className="w-4 h-4" />
                          Top Performers
                        </h4>
                        <div className="space-y-2">
                          {topPerformers.map((result, index) => (
                            <div key={result.employee_id} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                              <div className="flex items-center gap-3">
                                <Badge variant="outline" className="w-8 h-8 rounded-full flex items-center justify-center">
                                  {index + 1}
                                </Badge>
                                <div>
                                  <div className="font-medium">{result.employee_name}</div>
                                  <div className="text-sm text-gray-500">
                                    {new Date(result.calculation_date).toLocaleDateString()}
                                  </div>
                                </div>
                              </div>
                              <Badge className="bg-green-100 text-green-700">
                                {result.calculated_value.toFixed(2)}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold text-red-700 mb-3 flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4" />
                          Needs Attention
                        </h4>
                        <div className="space-y-2">
                          {bottomPerformers.map((result, index) => (
                            <div key={result.employee_id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                              <div className="flex items-center gap-3">
                                <Badge variant="outline" className="w-8 h-8 rounded-full flex items-center justify-center">
                                  {index + 1}
                                </Badge>
                                <div>
                                  <div className="font-medium">{result.employee_name}</div>
                                  <div className="text-sm text-gray-500">
                                    {new Date(result.calculation_date).toLocaleDateString()}
                                  </div>
                                </div>
                              </div>
                              <Badge className="bg-red-100 text-red-700">
                                {result.calculated_value.toFixed(2)}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </TabsContent>

          <TabsContent value="components" className="space-y-6">
            {kpiDefinitions.map((kpi) => {
              const IconComponent = kpiIcons[kpi.kpi_code as keyof typeof kpiIcons];
              const sampleResult = kpiResults.find(r => r.kpi_code === kpi.kpi_code);
              
              return (
                <Card key={kpi.kpi_code}>
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <IconComponent 
                        className="w-5 h-5" 
                        style={{ color: kpiColors[kpi.kpi_code as keyof typeof kpiColors] }}
                      />
                      <CardTitle>{kpi.name} - Component Analysis</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-semibold mb-3">Formula Breakdown</h4>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <code className="text-sm">{kpi.formula_expression}</code>
                        </div>
                        
                        <div className="mt-4 space-y-2">
                          <h5 className="font-medium">Parameter Weights:</h5>
                          {Object.entries(kpi.parameter_weights).map(([param, weight]) => (
                            <div key={param} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                              <span className="text-sm font-medium">{param}</span>
                              <Badge variant="outline">{(weight * 100).toFixed(0)}%</Badge>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      {sampleResult && (
                        <div>
                          <h4 className="font-semibold mb-3">Sample Component Scores</h4>
                          <div className="space-y-3">
                            {Object.entries(sampleResult.component_scores).map(([param, score]) => (
                              <div key={param} className="space-y-1">
                                <div className="flex justify-between items-center">
                                  <span className="text-sm font-medium">{param}</span>
                                  <Badge className={`${getScoreColor(score as number)}`}>
                                    {(score as number).toFixed(1)}
                                  </Badge>
                                </div>
                                <Progress value={(score as number) * 20} className="h-2" />
                              </div>
                            ))}
                          </div>
                          
                          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                            <div className="text-sm text-blue-700">
                              <strong>Final Score: {sampleResult.calculated_value.toFixed(2)}</strong>
                            </div>
                            <div className="text-xs text-blue-600 mt-1">
                              Employee: {sampleResult.employee_name}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdvancedKPIDashboard; 