import React, { useState, useEffect } from 'react';

interface MobileCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: number;
  icon?: string;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
  onClick?: () => void;
}

export function MobileCard({ title, value, subtitle, trend, trendValue, icon, color = 'blue', onClick }: MobileCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-800',
    green: 'bg-green-50 border-green-200 text-green-800',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    red: 'bg-red-50 border-red-200 text-red-800',
    purple: 'bg-purple-50 border-purple-200 text-purple-800'
  };

  const getTrendIcon = () => {
    if (!trend || !trendValue) return null;
    if (trend === 'up') return <span className="text-green-500 text-sm">↗ +{trendValue}%</span>;
    if (trend === 'down') return <span className="text-red-500 text-sm">↘ {trendValue}%</span>;
    return <span className="text-gray-500 text-sm">→ {trendValue}%</span>;
  };

  return (
    <div 
      className={`p-4 rounded-lg border shadow-sm ${colorClasses[color]} ${onClick ? 'cursor-pointer hover:shadow-md' : ''} transition-all`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-2">
        {icon && <span className="text-xl">{icon}</span>}
        <h3 className="text-sm font-medium text-gray-700 flex-1 ml-2">{title}</h3>
        {getTrendIcon()}
      </div>
      <div className="flex items-baseline">
        <span className="text-2xl font-bold text-gray-900">{value}</span>
        {subtitle && <span className="ml-2 text-sm text-gray-600">{subtitle}</span>}
      </div>
    </div>
  );
}

interface MobileTabsProps {
  tabs: Array<{
    id: string;
    label: string;
    icon?: string;
  }>;
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

export function MobileTabs({ tabs, activeTab, onTabChange }: MobileTabsProps) {
  return (
    <div className="flex overflow-x-auto bg-gray-100 rounded-lg p-1 mb-6">
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`flex items-center px-4 py-2 rounded-md whitespace-nowrap transition-colors ${
            activeTab === tab.id 
              ? 'bg-white shadow-sm text-blue-600' 
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          {tab.icon && <span className="mr-2">{tab.icon}</span>}
          {tab.label}
        </button>
      ))}
    </div>
  );
}

interface MobileListItemProps {
  title: string;
  subtitle?: string;
  value?: string;
  status?: 'active' | 'inactive' | 'pending' | 'completed';
  icon?: string;
  rightElement?: React.ReactNode;
  onClick?: () => void;
}

export function MobileListItem({ title, subtitle, value, status, icon, rightElement, onClick }: MobileListItemProps) {
  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      default: return '';
    }
  };

  return (
    <div 
      className={`flex items-center p-4 bg-white border border-gray-200 rounded-lg mb-2 ${onClick ? 'cursor-pointer hover:bg-gray-50' : ''}`}
      onClick={onClick}
    >
      {icon && <span className="text-xl mr-3">{icon}</span>}
      <div className="flex-1">
        <h4 className="font-medium text-gray-900">{title}</h4>
        {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
        {status && (
          <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium mt-1 ${getStatusColor(status)}`}>
            {status.toUpperCase()}
          </span>
        )}
      </div>
      {value && <span className="text-lg font-semibold text-gray-900 ml-2">{value}</span>}
      {rightElement}
    </div>
  );
}

interface MobileActionButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  onClick?: () => void;
  disabled?: boolean;
}

export function MobileActionButton({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  fullWidth = false, 
  onClick, 
  disabled = false 
}: MobileActionButtonProps) {
  const baseClasses = 'font-medium rounded-lg transition-colors flex items-center justify-center';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-300',
    secondary: 'bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:bg-gray-50',
    danger: 'bg-red-600 text-white hover:bg-red-700 disabled:bg-red-300'
  };

  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2.5 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  const widthClass = fullWidth ? 'w-full' : '';

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${widthClass}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

interface MobileHeaderProps {
  title: string;
  subtitle?: string;
  backButton?: boolean;
  onBack?: () => void;
  rightElement?: React.ReactNode;
}

export function MobileHeader({ title, subtitle, backButton = false, onBack, rightElement }: MobileHeaderProps) {
  return (
    <div className="bg-white border-b border-gray-200 px-4 py-4 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          {backButton && (
            <button 
              onClick={onBack}
              className="mr-3 p-2 rounded-full hover:bg-gray-100 transition-colors"
            >
              ←
            </button>
          )}
          <div>
            <h1 className="text-xl font-bold text-gray-900">{title}</h1>
            {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
          </div>
        </div>
        {rightElement}
      </div>
    </div>
  );
}

interface MobileBottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export function MobileBottomSheet({ isOpen, onClose, title, children }: MobileBottomSheetProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
    
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 lg:hidden">
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose} />
      <div className="absolute bottom-0 left-0 right-0 bg-white rounded-t-xl max-h-[80vh] overflow-y-auto">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
            <button 
              onClick={onClose}
              className="p-2 rounded-full hover:bg-gray-100 transition-colors"
            >
              ✕
            </button>
          </div>
        </div>
        <div className="p-4">
          {children}
        </div>
      </div>
    </div>
  );
}

export function useResponsiveDesign() {
  const [isMobile, setIsMobile] = useState(false);
  const [isTablet, setIsTablet] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 768);
      setIsTablet(window.innerWidth >= 768 && window.innerWidth < 1024);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  return { isMobile, isTablet, isDesktop: !isMobile && !isTablet };
}

// Mobile Dashboard Example
export function MobileDashboardExample() {
  const [activeTab, setActiveTab] = useState('overview');
  const [showBottomSheet, setShowBottomSheet] = useState(false);
  const { isMobile } = useResponsiveDesign();

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'team', label: 'Team', icon: '👥' },
    { id: 'alerts', label: 'Alerts', icon: '🚨' }
  ];

  const kpiData = [
    { title: 'Engagement', value: '78%', trend: 'up' as const, trendValue: 2.3, icon: '💝', color: 'blue' as const },
    { title: 'Performance', value: '4.2', subtitle: '/5.0', trend: 'up' as const, trendValue: 0.15, icon: '📈', color: 'green' as const },
    { title: 'Turnover', value: '8.2%', trend: 'down' as const, trendValue: -1.1, icon: '🔄', color: 'yellow' as const },
    { title: 'Satisfaction', value: '85%', trend: 'stable' as const, trendValue: 0, icon: '😊', color: 'purple' as const }
  ];

  const teamData = [
    { title: 'Engineering', subtitle: '45 employees', value: '78%', status: 'active' as const, icon: '💻' },
    { title: 'Sales', subtitle: '32 employees', value: '85%', status: 'active' as const, icon: '💼' },
    { title: 'Marketing', subtitle: '18 employees', value: '72%', status: 'pending' as const, icon: '📱' }
  ];

  if (!isMobile) {
    return (
      <div className="p-8 text-center">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Mobile Components Preview</h2>
        <p className="text-gray-600 mb-4">These components are optimized for mobile devices. Resize your browser to see them in action.</p>
        <div className="max-w-sm mx-auto border border-gray-300 rounded-lg p-4">
          <MobileHeader title="HR Dashboard" subtitle="Mobile Preview" />
          <div className="space-y-4">
            <MobileCard 
              title="Sample Metric" 
              value="85%" 
              trend="up" 
              trendValue={2.5} 
              icon="📊" 
              color="blue"
            />
            <MobileListItem 
              title="Sample Department" 
              subtitle="20 employees" 
              value="92%" 
              status="active" 
              icon="👥"
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <MobileHeader 
        title="HR Dashboard" 
        subtitle="Real-time insights"
        rightElement={
          <button 
            onClick={() => setShowBottomSheet(true)}
            className="p-2 rounded-full bg-blue-100 text-blue-600"
          >
            ⚙️
          </button>
        }
      />

      <div className="px-4">
        <MobileTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

        {activeTab === 'overview' && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {kpiData.map((kpi, index) => (
                <MobileCard key={index} {...kpi} />
              ))}
            </div>
            
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <MobileActionButton fullWidth variant="primary">
                  📋 Create Survey
                </MobileActionButton>
                <MobileActionButton fullWidth variant="secondary">
                  📊 View Analytics
                </MobileActionButton>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'team' && (
          <div className="space-y-2">
            {teamData.map((team, index) => (
              <MobileListItem key={index} {...team} />
            ))}
          </div>
        )}

        {activeTab === 'alerts' && (
          <div className="space-y-4">
            <MobileListItem 
              title="High Turnover Alert" 
              subtitle="Engineering department - 15 min ago" 
              status="pending"
              icon="🚨"
            />
            <MobileListItem 
              title="Survey Response Low" 
              subtitle="Q4 Engagement - 1 hour ago" 
              status="active"
              icon="⚠️"
            />
          </div>
        )}
      </div>

      <MobileBottomSheet 
        isOpen={showBottomSheet} 
        onClose={() => setShowBottomSheet(false)}
        title="Settings"
      >
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3">
            <span className="text-gray-900">Auto-refresh</span>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">ON</button>
          </div>
          <div className="flex items-center justify-between py-3">
            <span className="text-gray-900">Notifications</span>
            <button className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm">OFF</button>
          </div>
          <MobileActionButton fullWidth variant="danger">
            Sign Out
          </MobileActionButton>
        </div>
      </MobileBottomSheet>
    </div>
  );
} 