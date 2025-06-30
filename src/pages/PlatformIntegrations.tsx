import React, { useState } from 'react';

interface Integration {
  id: string;
  name: string;
  description: string;
  icon: string;
  status: 'connected' | 'disconnected' | 'pending';
  features: string[];
  lastSync?: string;
}

export function PlatformIntegrations() {
  const [integrations, setIntegrations] = useState<Integration[]>([
    {
      id: 'slack',
      name: 'Slack',
      description: 'Send survey invitations, notifications, and updates directly to Slack channels',
      icon: '💬',
      status: 'connected',
      features: ['Survey Notifications', 'Action Plan Updates', 'Performance Alerts', 'Team Mentions'],
      lastSync: '2024-01-15T10:30:00Z'
    },
    {
      id: 'teams',
      name: 'Microsoft Teams',
      description: 'Integrate with Teams for seamless HR communications and collaboration',
      icon: '👥',
      status: 'disconnected',
      features: ['Meeting Invites', 'Survey Distribution', 'Team Notifications', 'File Sharing']
    },
    {
      id: 'outlook',
      name: 'Microsoft Outlook',
      description: 'Sync calendar events, send email reminders, and manage HR communications',
      icon: '📧',
      status: 'connected',
      features: ['Email Notifications', 'Calendar Integration', 'Meeting Reminders', 'Performance Reviews'],
      lastSync: '2024-01-15T09:15:00Z'
    },
    {
      id: 'bamboohr',
      name: 'BambooHR',
      description: 'Connect with BambooHR for employee data synchronization',
      icon: '🎋',
      status: 'pending',
      features: ['Employee Data Sync', 'Performance Records', 'Time Off Integration', 'Org Chart Updates']
    },
    {
      id: 'workday',
      name: 'Workday',
      description: 'Enterprise-grade integration with Workday HCM platform',
      icon: '💼',
      status: 'disconnected',
      features: ['HR Analytics', 'Employee Records', 'Payroll Integration', 'Compliance Tracking']
    },
    {
      id: 'zoom',
      name: 'Zoom',
      description: 'Schedule and manage HR meetings, interviews, and team sessions',
      icon: '📹',
      status: 'connected',
      features: ['Meeting Scheduling', 'Interview Management', 'Team Sessions', 'Recording Access'],
      lastSync: '2024-01-15T11:00:00Z'
    }
  ]);

  const [showIntegrationModal, setShowIntegrationModal] = useState(false);
  const [selectedIntegration, setSelectedIntegration] = useState<Integration | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-green-100 text-green-800 border-green-200';
      case 'disconnected': return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const handleConnect = (integration: Integration) => {
    setSelectedIntegration(integration);
    setShowIntegrationModal(true);
  };

  const handleDisconnect = (integrationId: string) => {
    setIntegrations(prev => 
      prev.map(int => 
        int.id === integrationId 
          ? { ...int, status: 'disconnected' as const, lastSync: undefined }
          : int
      )
    );
  };

  const mockConnectIntegration = (integrationId: string) => {
    setIntegrations(prev => 
      prev.map(int => 
        int.id === integrationId 
          ? { ...int, status: 'connected' as const, lastSync: new Date().toISOString() }
          : int
      )
    );
    setShowIntegrationModal(false);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🔗 Platform Integrations</h1>
          <p className="text-gray-600">Connect your HR dashboard with workplace tools and platforms</p>
        </div>
        <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
          + Add Integration
        </button>
      </div>

      {/* Integration Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <span className="text-2xl">✅</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600">Connected</h3>
              <p className="text-2xl font-bold text-green-600">
                {integrations.filter(i => i.status === 'connected').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <span className="text-2xl">⏳</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600">Pending</h3>
              <p className="text-2xl font-bold text-yellow-600">
                {integrations.filter(i => i.status === 'pending').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-gray-100 rounded-lg">
              <span className="text-2xl">📊</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600">Available</h3>
              <p className="text-2xl font-bold text-gray-600">
                {integrations.length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Integrations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {integrations.map(integration => (
          <div key={integration.id} className="bg-white rounded-lg shadow border p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center">
                <span className="text-3xl mr-3">{integration.icon}</span>
                <div>
                  <h3 className="font-semibold text-gray-900">{integration.name}</h3>
                  <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(integration.status)}`}>
                    {integration.status.charAt(0).toUpperCase() + integration.status.slice(1)}
                  </span>
                </div>
              </div>
            </div>
            
            <p className="text-sm text-gray-600 mb-4">{integration.description}</p>
            
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Features:</h4>
              <div className="flex flex-wrap gap-1">
                {integration.features.map((feature, index) => (
                  <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    {feature}
                  </span>
                ))}
              </div>
            </div>
            
            {integration.lastSync && (
              <p className="text-xs text-gray-500 mb-4">
                Last sync: {new Date(integration.lastSync).toLocaleString()}
              </p>
            )}
            
            <div className="flex space-x-2">
              {integration.status === 'connected' ? (
                <>
                  <button className="flex-1 bg-green-50 text-green-700 border border-green-200 px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-100 transition-colors">
                    ⚙️ Configure
                  </button>
                  <button 
                    onClick={() => handleDisconnect(integration.id)}
                    className="px-4 py-2 bg-red-50 text-red-700 border border-red-200 rounded-lg text-sm font-medium hover:bg-red-100 transition-colors"
                  >
                    🔌 Disconnect
                  </button>
                </>
              ) : (
                <button 
                  onClick={() => handleConnect(integration)}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
                >
                  🔗 Connect
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Integration Benefits */}
      <div className="mt-12 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">🚀 Benefits of Platform Integrations</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-4xl mb-3">⚡</div>
            <h3 className="font-semibold text-gray-900 mb-2">Automated Workflows</h3>
            <p className="text-sm text-gray-600">Reduce manual work with automated notifications and data sync</p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-3">📈</div>
            <h3 className="font-semibold text-gray-900 mb-2">Better Engagement</h3>
            <p className="text-sm text-gray-600">Reach employees where they already work and collaborate</p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-3">🎯</div>
            <h3 className="font-semibold text-gray-900 mb-2">Centralized Data</h3>
            <p className="text-sm text-gray-600">Keep all HR data synchronized across platforms</p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-3">💡</div>
            <h3 className="font-semibold text-gray-900 mb-2">Smart Insights</h3>
            <p className="text-sm text-gray-600">Get deeper insights by combining data from multiple sources</p>
          </div>
        </div>
      </div>

      {/* Integration Modal */}
      {showIntegrationModal && selectedIntegration && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex items-center mb-4">
              <span className="text-3xl mr-3">{selectedIntegration.icon}</span>
              <h2 className="text-xl font-bold text-gray-900">Connect {selectedIntegration.name}</h2>
            </div>
            
            <p className="text-gray-600 mb-6">{selectedIntegration.description}</p>
            
            <div className="mb-6">
              <h3 className="font-medium text-gray-900 mb-2">You'll be able to:</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                {selectedIntegration.features.map((feature, index) => (
                  <li key={index} className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="flex space-x-3">
              <button 
                onClick={() => mockConnectIntegration(selectedIntegration.id)}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                Connect Now
              </button>
              <button 
                onClick={() => setShowIntegrationModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 