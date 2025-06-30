import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Star, Brain, TrendingUp, Users, Shield, Plus, Filter, ChevronDown, BarChart3, Calendar, User, Eye, Edit, Trash2 } from 'lucide-react';
import api from '@/api';

interface ParameterDefinition {
  parameter_id: string;
  name: string;
  category: string;
  definition: string;
  relevance_summary: string;
  behavioral_anchors: {
    scale: string;
    anchors: Array<{
      rating_value: number;
      level_descriptor: string;
      indicators: string[];
    }>;
  };
  is_active: boolean;
}

interface ParameterRating {
  id: string;
  employee_id: string;
  employee_name: string;
  parameter_id: string;
  parameter_name: string;
  rating_value: number;
  rater_type: string;
  evidence_text?: string;
  confidence_score: number;
  rating_period_start: string;
  rating_period_end: string;
  created_at: string;
}

interface Employee {
  id: string;
  name: string;
  email: string;
  position: string;
  department_id: string;
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

const ParameterManagement: React.FC = () => {
  const [parameters, setParameters] = useState<ParameterDefinition[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [ratings, setRatings] = useState<ParameterRating[]>([]);
  const [kpiResults, setKpiResults] = useState<KPIResult[]>([]);
  const [selectedEmployee, setSelectedEmployee] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [activeTab, setActiveTab] = useState('parameters');
  const [loading, setLoading] = useState(false);
  const [ratingFormOpen, setRatingFormOpen] = useState(false);
  const [selectedParameter, setSelectedParameter] = useState<ParameterDefinition | null>(null);

  // Form states
  const [ratingForm, setRatingForm] = useState({
    employee_id: '',
    parameter_id: '',
    rating_value: 3,
    rater_type: 'manager',
    evidence_text: '',
    confidence_score: 1.0,
    rating_period_start: new Date().toISOString().split('T')[0],
    rating_period_end: new Date().toISOString().split('T')[0]
  });

  const categoryIcons = {
    'COGNITIVE_MOTIVATIONAL': Brain,
    'EMOTIONAL_SOCIAL': Users,
    'PERFORMANCE_ADAPTABILITY': TrendingUp,
    'ETHICAL_MODERN_WORKPLACE': Shield
  };

  const categoryColors = {
    'COGNITIVE_MOTIVATIONAL': 'bg-blue-500',
    'EMOTIONAL_SOCIAL': 'bg-green-500',
    'PERFORMANCE_ADAPTABILITY': 'bg-orange-500',
    'ETHICAL_MODERN_WORKPLACE': 'bg-purple-500'
  };

  useEffect(() => {
    loadParameters();
    loadEmployees();
  }, []);

  useEffect(() => {
    if (selectedEmployee) {
      loadEmployeeRatings(selectedEmployee);
      loadEmployeeKPIs(selectedEmployee);
    }
  }, [selectedEmployee]);

  const loadParameters = async () => {
    try {
      setLoading(true);
      const response = await api.get('/parameters/definitions');
      setParameters(response.data);
    } catch (error) {
      console.error('Failed to load parameters:', error);
    } finally {
      setLoading(false);
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

  const loadEmployeeRatings = async (employeeId: string) => {
    try {
      const response = await api.get(`/parameters/employees/${employeeId}/ratings`);
      setRatings(response.data);
    } catch (error) {
      console.error('Failed to load employee ratings:', error);
    }
  };

  const loadEmployeeKPIs = async (employeeId: string) => {
    try {
      const response = await api.get(`/parameters/kpis/employees/${employeeId}`);
      setKpiResults(response.data);
    } catch (error) {
      console.error('Failed to load employee KPIs:', error);
    }
  };

  const submitRating = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      await api.post('/parameters/ratings', ratingForm);
      setRatingFormOpen(false);
      if (selectedEmployee) {
        loadEmployeeRatings(selectedEmployee);
      }
      // Reset form
      setRatingForm({
        employee_id: '',
        parameter_id: '',
        rating_value: 3,
        rater_type: 'manager',
        evidence_text: '',
        confidence_score: 1.0,
        rating_period_start: new Date().toISOString().split('T')[0],
        rating_period_end: new Date().toISOString().split('T')[0]
      });
    } catch (error) {
      console.error('Failed to submit rating:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateKPIs = async () => {
    if (!selectedEmployee) return;
    
    try {
      setLoading(true);
      await api.post('/parameters/kpis/calculate/bulk');
      loadEmployeeKPIs(selectedEmployee);
    } catch (error) {
      console.error('Failed to calculate KPIs:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredParameters = parameters.filter(param => 
    selectedCategory === 'all' || param.category === selectedCategory
  );

  const getRatingColor = (rating: number) => {
    if (rating >= 4.5) return 'text-green-600 bg-green-100';
    if (rating >= 3.5) return 'text-blue-600 bg-blue-100';
    if (rating >= 2.5) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getParameterStats = (parameterId: string) => {
    const paramRatings = ratings.filter(r => r.parameter_id === parameterId);
    if (paramRatings.length === 0) return null;
    
    const avgRating = paramRatings.reduce((sum, r) => sum + r.rating_value, 0) / paramRatings.length;
    const avgConfidence = paramRatings.reduce((sum, r) => sum + r.confidence_score, 0) / paramRatings.length;
    
    return { avgRating, avgConfidence, count: paramRatings.length };
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Parameter Management System</h1>
            <p className="text-gray-600 mt-1">Comprehensive 35-parameter employee evaluation framework</p>
          </div>
          <div className="flex gap-3">
            <Dialog open={ratingFormOpen} onOpenChange={setRatingFormOpen}>
              <DialogTrigger asChild>
                <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Rating
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Create Parameter Rating</DialogTitle>
                </DialogHeader>
                <form onSubmit={submitRating} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Employee</label>
                      <Select value={ratingForm.employee_id} onValueChange={(value) => setRatingForm({...ratingForm, employee_id: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select employee" />
                        </SelectTrigger>
                        <SelectContent>
                          {employees.map(emp => (
                            <SelectItem key={emp.id} value={emp.id}>
                              {emp.name} - {emp.position}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Parameter</label>
                      <Select value={ratingForm.parameter_id} onValueChange={(value) => setRatingForm({...ratingForm, parameter_id: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select parameter" />
                        </SelectTrigger>
                        <SelectContent>
                          {parameters.map(param => (
                            <SelectItem key={param.parameter_id} value={param.parameter_id}>
                              {param.parameter_id} - {param.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Rating (1-5)</label>
                      <Input
                        type="number"
                        min="1"
                        max="5"
                        step="0.1"
                        value={ratingForm.rating_value}
                        onChange={(e) => setRatingForm({...ratingForm, rating_value: parseFloat(e.target.value)})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Rater Type</label>
                      <Select value={ratingForm.rater_type} onValueChange={(value) => setRatingForm({...ratingForm, rater_type: value})}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="self">Self</SelectItem>
                          <SelectItem value="manager">Manager</SelectItem>
                          <SelectItem value="peer">Peer</SelectItem>
                          <SelectItem value="system">System</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Confidence</label>
                      <Input
                        type="number"
                        min="0"
                        max="1"
                        step="0.1"
                        value={ratingForm.confidence_score}
                        onChange={(e) => setRatingForm({...ratingForm, confidence_score: parseFloat(e.target.value)})}
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Evidence/Notes</label>
                    <Textarea
                      value={ratingForm.evidence_text}
                      onChange={(e) => setRatingForm({...ratingForm, evidence_text: e.target.value})}
                      placeholder="Provide specific behavioral examples or evidence for this rating..."
                      rows={3}
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Period Start</label>
                      <Input
                        type="date"
                        value={ratingForm.rating_period_start}
                        onChange={(e) => setRatingForm({...ratingForm, rating_period_start: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Period End</label>
                      <Input
                        type="date"
                        value={ratingForm.rating_period_end}
                        onChange={(e) => setRatingForm({...ratingForm, rating_period_end: e.target.value})}
                      />
                    </div>
                  </div>
                  
                  <div className="flex justify-end gap-3 pt-4">
                    <Button type="button" variant="outline" onClick={() => setRatingFormOpen(false)}>
                      Cancel
                    </Button>
                    <Button type="submit" disabled={loading}>
                      {loading ? 'Creating...' : 'Create Rating'}
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>

            <Button onClick={calculateKPIs} disabled={!selectedEmployee || loading} variant="outline">
              <BarChart3 className="w-4 h-4 mr-2" />
              Calculate KPIs
            </Button>
          </div>
        </div>

        {/* Employee Selection */}
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <User className="w-5 h-5 text-gray-500" />
              <Select value={selectedEmployee} onValueChange={setSelectedEmployee}>
                <SelectTrigger className="w-80">
                  <SelectValue placeholder="Select employee to view/manage parameters" />
                </SelectTrigger>
                <SelectContent>
                  {employees.map(emp => (
                    <SelectItem key={emp.id} value={emp.id}>
                      <div className="flex flex-col">
                        <span className="font-medium">{emp.name}</span>
                        <span className="text-sm text-gray-500">{emp.position}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-60">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  <SelectItem value="COGNITIVE_MOTIVATIONAL">Cognitive & Motivational</SelectItem>
                  <SelectItem value="EMOTIONAL_SOCIAL">Emotional & Social</SelectItem>
                  <SelectItem value="PERFORMANCE_ADAPTABILITY">Performance & Adaptability</SelectItem>
                  <SelectItem value="ETHICAL_MODERN_WORKPLACE">Ethical & Modern Workplace</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="parameters">Parameters Overview</TabsTrigger>
            <TabsTrigger value="ratings">Current Ratings</TabsTrigger>
            <TabsTrigger value="kpis">Advanced KPIs</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="parameters" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredParameters.map((param) => {
                const IconComponent = categoryIcons[param.category as keyof typeof categoryIcons];
                const stats = selectedEmployee ? getParameterStats(param.parameter_id) : null;
                
                return (
                  <Card key={param.parameter_id} className="hover:shadow-lg transition-shadow">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          <div className={`p-2 rounded-lg ${categoryColors[param.category as keyof typeof categoryColors]}`}>
                            <IconComponent className="w-4 h-4 text-white" />
                          </div>
                          <div>
                            <CardTitle className="text-sm font-semibold text-gray-900">
                              {param.parameter_id}
                            </CardTitle>
                            <Badge variant="secondary" className="text-xs mt-1">
                              {param.category.replace('_', ' & ')}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    </CardHeader>
                    
                    <CardContent className="space-y-4">
                      <div>
                        <h3 className="font-semibold text-sm text-gray-900 mb-1">
                          {param.name}
                        </h3>
                        <p className="text-xs text-gray-600 leading-relaxed">
                          {param.definition.slice(0, 120)}...
                        </p>
                      </div>
                      
                      <div className="bg-blue-50 p-3 rounded-lg">
                        <p className="text-xs text-blue-700 font-medium">Relevance:</p>
                        <p className="text-xs text-blue-600 mt-1">{param.relevance_summary}</p>
                      </div>
                      
                      {stats && (
                        <div className="space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="text-xs font-medium text-gray-700">Current Rating</span>
                            <Badge className={`text-xs ${getRatingColor(stats.avgRating)}`}>
                              {stats.avgRating.toFixed(1)}/5.0
                            </Badge>
                          </div>
                          <Progress value={stats.avgRating * 20} className="h-2" />
                          <div className="flex justify-between text-xs text-gray-500">
                            <span>Confidence: {(stats.avgConfidence * 100).toFixed(0)}%</span>
                            <span>{stats.count} ratings</span>
                          </div>
                        </div>
                      )}
                      
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button variant="outline" size="sm" className="w-full" onClick={() => setSelectedParameter(param)}>
                            <Eye className="w-4 h-4 mr-2" />
                            View Details
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-4xl">
                          <DialogHeader>
                            <DialogTitle className="flex items-center gap-2">
                              <div className={`p-2 rounded-lg ${categoryColors[param.category as keyof typeof categoryColors]}`}>
                                <IconComponent className="w-4 h-4 text-white" />
                              </div>
                              {param.parameter_id}: {param.name}
                            </DialogTitle>
                          </DialogHeader>
                          
                          <div className="space-y-6">
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-2">Definition</h4>
                              <p className="text-gray-700">{param.definition}</p>
                            </div>
                            
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-2">Relevance</h4>
                              <p className="text-gray-700">{param.relevance_summary}</p>
                            </div>
                            
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-3">Behavioral Anchors (1-5 Scale)</h4>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {param.behavioral_anchors.anchors.map((anchor, index) => (
                                  <div key={index} className={`p-4 rounded-lg border-2 ${
                                    anchor.rating_value === 1 ? 'border-red-200 bg-red-50' :
                                    anchor.rating_value === 5 ? 'border-green-200 bg-green-50' :
                                    'border-gray-200 bg-gray-50'
                                  }`}>
                                    <div className="flex items-center gap-2 mb-2">
                                      <Badge variant="outline" className={
                                        anchor.rating_value === 1 ? 'border-red-300 text-red-700' :
                                        anchor.rating_value === 5 ? 'border-green-300 text-green-700' :
                                        'border-gray-300 text-gray-700'
                                      }>
                                        Level {anchor.rating_value}
                                      </Badge>
                                      <span className="font-medium text-sm">{anchor.level_descriptor}</span>
                                    </div>
                                    <ul className="text-sm text-gray-600 space-y-1">
                                      {anchor.indicators.map((indicator, idx) => (
                                        <li key={idx} className="flex items-start gap-2">
                                          <span className="text-gray-400 mt-1">•</span>
                                          {indicator}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>

          <TabsContent value="ratings" className="space-y-6">
            {selectedEmployee ? (
              <Card>
                <CardHeader>
                  <CardTitle>Current Parameter Ratings</CardTitle>
                  <p className="text-gray-600">
                    Employee: {employees.find(e => e.id === selectedEmployee)?.name}
                  </p>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Parameter</TableHead>
                        <TableHead>Category</TableHead>
                        <TableHead>Rating</TableHead>
                        <TableHead>Rater</TableHead>
                        <TableHead>Confidence</TableHead>
                        <TableHead>Period</TableHead>
                        <TableHead>Evidence</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {ratings.map((rating) => (
                        <TableRow key={rating.id}>
                          <TableCell>
                            <div>
                              <div className="font-medium">{rating.parameter_id}</div>
                              <div className="text-sm text-gray-500">{rating.parameter_name}</div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary" className="text-xs">
                              {parameters.find(p => p.parameter_id === rating.parameter_id)?.category.replace('_', ' & ')}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge className={`${getRatingColor(rating.rating_value)}`}>
                              {rating.rating_value.toFixed(1)}/5.0
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{rating.rater_type}</Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Progress value={rating.confidence_score * 100} className="w-16 h-2" />
                              <span className="text-sm">{(rating.confidence_score * 100).toFixed(0)}%</span>
                            </div>
                          </TableCell>
                          <TableCell className="text-sm text-gray-600">
                            {new Date(rating.rating_period_start).toLocaleDateString()} - {new Date(rating.rating_period_end).toLocaleDateString()}
                          </TableCell>
                          <TableCell className="max-w-xs">
                            {rating.evidence_text && (
                              <div className="text-sm text-gray-600 truncate" title={rating.evidence_text}>
                                {rating.evidence_text}
                              </div>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            ) : (
              <Alert>
                <AlertDescription>
                  Please select an employee to view their parameter ratings.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>

          <TabsContent value="kpis" className="space-y-6">
            {selectedEmployee ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {kpiResults.map((kpi) => (
                  <Card key={kpi.kpi_code} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <CardTitle className="text-lg">{kpi.kpi_name}</CardTitle>
                      <Badge variant="secondary">{kpi.kpi_code}</Badge>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-blue-600">
                          {kpi.calculated_value.toFixed(2)}
                        </div>
                        <div className="text-sm text-gray-500">Current Score</div>
                      </div>
                      
                      <Progress value={kpi.calculated_value * 20} className="h-3" />
                      
                      <div className="space-y-2">
                        <h4 className="font-semibold text-sm">Component Scores:</h4>
                        {Object.entries(kpi.component_scores).map(([param, score]) => (
                          <div key={param} className="flex justify-between items-center text-sm">
                            <span className="text-gray-600">{param}</span>
                            <Badge className={`${getRatingColor(score as number)}`}>
                              {(score as number).toFixed(1)}
                            </Badge>
                          </div>
                        ))}
                      </div>
                      
                      <div className="text-xs text-gray-500 pt-2 border-t">
                        <div>Calculated: {new Date(kpi.calculation_date).toLocaleDateString()}</div>
                        <div>Period: {new Date(kpi.period_start).toLocaleDateString()} - {new Date(kpi.period_end).toLocaleDateString()}</div>
                        <div>Confidence: {(kpi.confidence_score * 100).toFixed(0)}%</div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Alert>
                <AlertDescription>
                  Please select an employee to view their KPI calculations.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Total Parameters</p>
                      <p className="text-2xl font-bold text-gray-900">{parameters.length}</p>
                    </div>
                    <Brain className="w-8 h-8 text-blue-600" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Active Ratings</p>
                      <p className="text-2xl font-bold text-gray-900">{ratings.length}</p>
                    </div>
                    <Star className="w-8 h-8 text-yellow-600" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">KPI Results</p>
                      <p className="text-2xl font-bold text-gray-900">{kpiResults.length}</p>
                    </div>
                    <BarChart3 className="w-8 h-8 text-green-600" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Avg Rating</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {ratings.length > 0 ? (ratings.reduce((sum, r) => sum + r.rating_value, 0) / ratings.length).toFixed(1) : '0.0'}
                      </p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-purple-600" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ParameterManagement; 