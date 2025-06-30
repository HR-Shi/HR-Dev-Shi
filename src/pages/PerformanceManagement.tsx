import React, { useState } from 'react';

export function PerformanceManagement() {
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'Performance Overview', icon: '📊' },
    { id: 'reviews', label: 'Performance Reviews', icon: '📝' },
    { id: 'goals', label: 'Goals & Objectives', icon: '🎯' },
    { id: 'feedback', label: '360° Feedback', icon: '🔄' },
    { id: 'analytics', label: 'Performance Analytics', icon: '📈' }
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🏆 Performance Management</h1>
          <p className="text-gray-600">Comprehensive performance tracking, reviews, and development planning</p>
        </div>
        <div className="flex space-x-3">
          <button className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all flex items-center shadow-lg">
            <span className="mr-2">🔄</span>
            Request 360° Feedback
          </button>
          <button className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors flex items-center">
            <span className="mr-2">📝</span>
            Create Review
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-8 bg-gray-100 p-1 rounded-lg">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center px-4 py-2 rounded-md transition-colors ${
              activeTab === tab.id 
                ? 'bg-white shadow-sm text-blue-600' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-3 bg-green-100 rounded-lg">
                  <span className="text-2xl">🏆</span>
                </div>
                <div className="ml-4">
                  <h3 className="text-sm font-medium text-gray-600">High Performers</h3>
                  <p className="text-2xl font-bold text-green-600">12</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <span className="text-2xl">📈</span>
                </div>
                <div className="ml-4">
                  <h3 className="text-sm font-medium text-gray-600">Avg Performance</h3>
                  <p className="text-2xl font-bold text-blue-600">4.2</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <span className="text-2xl">📝</span>
                </div>
                <div className="ml-4">
                  <h3 className="text-sm font-medium text-gray-600">Pending Reviews</h3>
                  <p className="text-2xl font-bold text-purple-600">8</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-3 bg-orange-100 rounded-lg">
                  <span className="text-2xl">🎯</span>
                </div>
                <div className="ml-4">
                  <h3 className="text-sm font-medium text-gray-600">Goals Completed</h3>
                  <p className="text-2xl font-bold text-orange-600">85%</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🌟 Performance Management Features</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">📊 Performance Reviews</h4>
                <p className="text-sm text-gray-600">Comprehensive review cycles with AI insights and calibration tools</p>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">🎯 Goal Management</h4>
                <p className="text-sm text-gray-600">Set, track, and measure employee goals with progress monitoring</p>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">🔄 360° Feedback</h4>
                <p className="text-sm text-gray-600">Multi-source feedback collection and analysis</p>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">📈 Performance Analytics</h4>
                <p className="text-sm text-gray-600">Data-driven insights and performance trends</p>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">🤖 AI Insights</h4>
                <p className="text-sm text-gray-600">AI-powered performance recommendations and predictions</p>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">🏅 Recognition</h4>
                <p className="text-sm text-gray-600">Peer recognition and achievement tracking</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Other tabs content */}
      {activeTab !== 'overview' && (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <span className="text-6xl mb-4 block">{tabs.find(t => t.id === activeTab)?.icon}</span>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {tabs.find(t => t.id === activeTab)?.label} - Coming Soon
          </h3>
          <p className="text-gray-600">This feature is being developed with advanced AI capabilities.</p>
        </div>
      )}
    </div>
  );
} 