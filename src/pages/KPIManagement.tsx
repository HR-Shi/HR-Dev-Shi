import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../api';

interface KPI {
  id: string;
  name: string;
  description: string;
  category: string;
  target_value: number;
  current_value: number;
  unit: string;
  measurement_frequency: string;
  calculation_method: string;
  is_custom: boolean;
  is_active: boolean;
  target_departments: string[];
  target_employee_groups: string[];
  alert_threshold_low?: number;
  alert_threshold_high?: number;
  created_by: string;
  created_at: string;
  updated_at: string;
}

interface PredefinedKPI {
  name: string;
  description: string;
  measurement_type: string;
  default_target: number;
  frequency: string;
  calculation_method: string;
}

interface KPIMeasurement {
  id: string;
  kpi_id: string;
  value: number;
  measurement_date: string;
  notes?: string;
}

export function KPIManagement() {
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [predefinedKpis, setPredefinedKpis] = useState<Record<string, PredefinedKPI[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Form states
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showPredefinedSelector, setShowPredefinedSelector] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedPredefinedKPI, setSelectedPredefinedKPI] = useState<PredefinedKPI | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: '',
    target_value: 0,
    unit: '%',
    measurement_frequency: 'monthly',
    calculation_method: '',
    alert_threshold_low: 0,
    alert_threshold_high: 0,
    target_departments: [],
    target_employee_groups: []
  });

  // Filter states
  const [filterCategory, setFilterCategory] = useState<string>('');
  const [filterActive, setFilterActive] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');

  const categories = [
    'Employee Engagement',
    'Turnover Rate', 
    'Training Effectiveness',
    'Diversity Metrics',
    'Performance Metrics',
    'Job Satisfaction',
    'Employee Wellness',
    'Productivity Metrics'
  ];

  const frequencies = [
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'quarterly', label: 'Quarterly' },
    { value: 'annually', label: 'Annually' }
  ];

  const units = [
    { value: '%', label: 'Percentage (%)' },
    { value: 'score', label: 'Score (1-5)' },
    { value: 'ratio', label: 'Ratio' },
    { value: 'count', label: 'Count' },
    { value: 'days', label: 'Days' },
    { value: 'hours', label: 'Hours' }
  ];

  useEffect(() => {
    fetchKPIs();
    fetchPredefinedKPIs();
  }, []);

  const fetchKPIs = async () => {
    try {
      setLoading(true);
      const data = await dashboardAPI.getKPIs();
      setKpis(data);
    } catch (error) {
      console.error('Error fetching KPIs:', error);
      setError('Failed to load KPIs');
    } finally {
      setLoading(false);
    }
  };

  const fetchPredefinedKPIs = async () => {
    try {
      const data = await dashboardAPI.getPredefinedKPIs();
      setPredefinedKpis(data.all_kpis || {});
    } catch (error) {
      console.error('Error fetching predefined KPIs:', error);
    }
  };

  const handleCreateKPI = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const newKPI = await dashboardAPI.createKPI({
        ...formData,
        is_custom: true,
        is_active: true
      });
      setKpis(prev => [...prev, newKPI]);
      setShowCreateForm(false);
      resetForm();
    } catch (error) {
      console.error('Error creating KPI:', error);
      setError('Failed to create KPI');
    }
  };

  const handleUsePredefinedKPI = async (predefinedKPI: PredefinedKPI) => {
    try {
      const newKPI = await dashboardAPI.createKPI({
        name: predefinedKPI.name,
        description: predefinedKPI.description,
        category: selectedCategory,
        target_value: predefinedKPI.default_target,
        unit: predefinedKPI.measurement_type === 'percentage' ? '%' : 'score',
        measurement_frequency: predefinedKPI.frequency,
        calculation_method: predefinedKPI.calculation_method,
        is_custom: false,
        is_active: true,
        alert_threshold_low: predefinedKPI.default_target * 0.8,
        alert_threshold_high: predefinedKPI.default_target * 1.2,
        target_departments: [],
        target_employee_groups: []
      });
      setKpis(prev => [...prev, newKPI]);
      setShowPredefinedSelector(false);
      setSelectedCategory('');
      setSelectedPredefinedKPI(null);
    } catch (error) {
      console.error('Error creating predefined KPI:', error);
      setError('Failed to create KPI from template');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      category: '',
      target_value: 0,
      unit: '%',
      measurement_frequency: 'monthly',
      calculation_method: '',
      alert_threshold_low: 0,
      alert_threshold_high: 0,
      target_departments: [],
      target_employee_groups: []
    });
  };

  const getKPIStatusColor = (kpi: KPI) => {
    if (!kpi.current_value || !kpi.target_value) return 'bg-gray-100 text-gray-800';
    
    const achievement = (kpi.current_value / kpi.target_value) * 100;
    if (achievement >= 95) return 'bg-green-100 text-green-800';
    if (achievement >= 80) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getKPIStatusText = (kpi: KPI) => {
    if (!kpi.current_value || !kpi.target_value) return 'No Data';
    
    const achievement = (kpi.current_value / kpi.target_value) * 100;
    if (achievement >= 95) return 'On Target';
    if (achievement >= 80) return 'Below Target';
    return 'Critical';
  };

  const filteredKPIs = kpis.filter(kpi => {
    const matchesCategory = !filterCategory || kpi.category === filterCategory;
    const matchesActive = kpi.is_active === filterActive;
    const matchesSearch = !searchTerm || 
      kpi.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      kpi.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesCategory && matchesActive && matchesSearch;
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">📊 KPI Management</h1>
          <p className="text-gray-600">Define and track Key Performance Indicators to measure organizational success</p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={() => setShowPredefinedSelector(true)}
            className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-2 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all flex items-center shadow-lg"
          >
            <span className="mr-2">📋</span>
            Add Predefined KPI
          </button>
          <button 
            onClick={() => setShowCreateForm(true)}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center"
          >
            <span className="mr-2">+</span>
            Create Custom KPI
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search KPIs</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by name or description..."
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={filterActive.toString()}
              onChange={(e) => setFilterActive(e.target.value === 'true')}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="true">Active KPIs</option>
              <option value="false">Inactive KPIs</option>
            </select>
          </div>
        </div>
      </div>

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <span className="text-2xl">📊</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600">Total KPIs</h3>
              <p className="text-2xl font-bold text-gray-900">{kpis.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <span className="text-2xl">✅</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600">On Target</h3>
              <p className="text-2xl font-bold text-green-600">
                {kpis.filter(kpi => kpi.current_value && kpi.target_value && (kpi.current_value / kpi.target_value) >= 0.95).length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <span className="text-2xl">⚠️</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600">Below Target</h3>
              <p className="text-2xl font-bold text-yellow-600">
                {kpis.filter(kpi => kpi.current_value && kpi.target_value && 
                  (kpi.current_value / kpi.target_value) >= 0.8 && (kpi.current_value / kpi.target_value) < 0.95).length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-red-100 rounded-lg">
              <span className="text-2xl">🚨</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600">Critical</h3>
              <p className="text-2xl font-bold text-red-600">
                {kpis.filter(kpi => kpi.current_value && kpi.target_value && (kpi.current_value / kpi.target_value) < 0.8).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* KPIs List */}
      <div className="space-y-6">
        {filteredKPIs.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
              <span className="text-4xl">📊</span>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No KPIs found</h3>
            <p className="text-gray-600 mb-4">Start by adding predefined KPIs or creating custom ones to track your organization's performance.</p>
            <button 
              onClick={() => setShowPredefinedSelector(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Add Your First KPI
            </button>
          </div>
        ) : (
          filteredKPIs.map((kpi) => (
            <div key={kpi.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-xl font-semibold text-gray-900">{kpi.name}</h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getKPIStatusColor(kpi)}`}>
                      {getKPIStatusText(kpi)}
                    </span>
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                      {kpi.category}
                    </span>
                    {kpi.is_custom && (
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                        CUSTOM
                      </span>
                    )}
                  </div>
                  <p className="text-gray-700 mb-4">{kpi.description}</p>
                  
                  {/* KPI Metrics */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-gray-600">Current Value</h4>
                      <p className="text-2xl font-bold text-gray-900">
                        {kpi.current_value ? `${kpi.current_value}${kpi.unit}` : 'No Data'}
                      </p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-gray-600">Target Value</h4>
                      <p className="text-2xl font-bold text-blue-600">
                        {kpi.target_value}${kpi.unit}
                      </p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-gray-600">Achievement</h4>
                      <p className="text-2xl font-bold text-green-600">
                        {kpi.current_value && kpi.target_value 
                          ? `${Math.round((kpi.current_value / kpi.target_value) * 100)}%`
                          : 'N/A'
                        }
                      </p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-gray-600">Frequency</h4>
                      <p className="text-lg font-semibold text-gray-900 capitalize">
                        {kpi.measurement_frequency}
                      </p>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  {kpi.current_value && kpi.target_value && (
                    <div className="mb-4">
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">Progress to Target</span>
                        <span className="text-gray-900 font-medium">
                          {Math.round((kpi.current_value / kpi.target_value) * 100)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div 
                          className={`h-3 rounded-full transition-all duration-300 ${
                            (kpi.current_value / kpi.target_value) >= 0.95 
                              ? 'bg-green-500' 
                              : (kpi.current_value / kpi.target_value) >= 0.8 
                                ? 'bg-yellow-500' 
                                : 'bg-red-500'
                          }`}
                          style={{ width: `${Math.min((kpi.current_value / kpi.target_value) * 100, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>📅 Created {new Date(kpi.created_at).toLocaleDateString()}</span>
                      <span>🔄 {kpi.measurement_frequency}</span>
                      <span>📊 {kpi.calculation_method}</span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-lg hover:bg-blue-200 transition-colors">
                        📈 View Analytics
                      </button>
                      <button className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-lg hover:bg-green-200 transition-colors">
                        📊 Add Measurement
                      </button>
                      <button className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 transition-colors">
                        ⚙️ Configure
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Predefined KPI Selector Modal */}
      {showPredefinedSelector && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">Select Predefined KPI</h2>
                <button
                  onClick={() => setShowPredefinedSelector(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
            </div>

            <div className="p-6">
              {!selectedCategory ? (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Choose a Category</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {categories.map(category => (
                      <button
                        key={category}
                        onClick={() => setSelectedCategory(category)}
                        className="p-4 text-left border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors"
                      >
                        <h4 className="font-semibold text-gray-900">{category}</h4>
                        <p className="text-sm text-gray-600 mt-1">
                          {predefinedKpis[category]?.length || 0} predefined KPIs available
                        </p>
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <div>
                  <div className="flex items-center mb-4">
                    <button
                      onClick={() => setSelectedCategory('')}
                      className="text-blue-600 hover:text-blue-800 mr-4"
                    >
                      ← Back to Categories
                    </button>
                    <h3 className="text-lg font-semibold text-gray-900">{selectedCategory}</h3>
                  </div>
                  
                  <div className="space-y-4">
                    {predefinedKpis[selectedCategory]?.map((predefinedKPI, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-900 mb-2">{predefinedKPI.name}</h4>
                            <p className="text-gray-600 mb-3">{predefinedKPI.description}</p>
                            <div className="flex space-x-4 text-sm text-gray-600">
                              <span>🎯 Target: {predefinedKPI.default_target}{predefinedKPI.measurement_type === 'percentage' ? '%' : ''}</span>
                              <span>📅 {predefinedKPI.frequency}</span>
                              <span>📊 {predefinedKPI.calculation_method}</span>
                            </div>
                          </div>
                          <button
                            onClick={() => handleUsePredefinedKPI(predefinedKPI)}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                          >
                            Add KPI
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Create Custom KPI Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto m-4">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">Create Custom KPI</h2>
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
            </div>

            <form onSubmit={handleCreateKPI} className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">KPI Name</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Employee Satisfaction Score"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                  <select
                    required
                    value={formData.category}
                    onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select Category</option>
                    {categories.map(category => (
                      <option key={category} value={category}>{category}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  required
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  rows={3}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Describe what this KPI measures and why it's important..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Target Value</label>
                  <input
                    type="number"
                    required
                    step="0.01"
                    value={formData.target_value}
                    onChange={(e) => setFormData(prev => ({ ...prev, target_value: parseFloat(e.target.value) }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="75"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Unit</label>
                  <select
                    value={formData.unit}
                    onChange={(e) => setFormData(prev => ({ ...prev, unit: e.target.value }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {units.map(unit => (
                      <option key={unit.value} value={unit.value}>{unit.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Frequency</label>
                  <select
                    value={formData.measurement_frequency}
                    onChange={(e) => setFormData(prev => ({ ...prev, measurement_frequency: e.target.value }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {frequencies.map(freq => (
                      <option key={freq.value} value={freq.value}>{freq.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Calculation Method</label>
                <input
                  type="text"
                  required
                  value={formData.calculation_method}
                  onChange={(e) => setFormData(prev => ({ ...prev, calculation_method: e.target.value }))}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., average_survey_score, percentage_calculation"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Low Alert Threshold</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.alert_threshold_low}
                    onChange={(e) => setFormData(prev => ({ ...prev, alert_threshold_low: parseFloat(e.target.value) }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="60"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">High Alert Threshold</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.alert_threshold_high}
                    onChange={(e) => setFormData(prev => ({ ...prev, alert_threshold_high: parseFloat(e.target.value) }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="90"
                  />
                </div>
              </div>

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
                  Create KPI
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
} 