import React from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { 
  Description as FileText, 
  Download, 
  CalendarToday as Calendar, 
  Person as User, 
  Search, 
  Add as Plus, 
  Visibility as Eye 
} from '@mui/icons-material';

const policies = [
  {
    id: 1,
    title: "Employee Handbook",
    description: "Comprehensive guide to company policies, procedures, and expectations",
    category: "General",
    lastUpdated: "2024-01-15",
    version: "3.2",
    status: "Active",
    size: "2.4 MB",
    downloads: 342
  },
  {
    id: 2,
    title: "Remote Work Policy",
    description: "Guidelines and requirements for remote work arrangements",
    category: "Work Arrangements",
    lastUpdated: "2024-01-10",
    version: "2.1",
    status: "Active",
    size: "1.2 MB",
    downloads: 156
  },
  {
    id: 3,
    title: "Code of Conduct",
    description: "Ethical standards and behavioral expectations for all employees",
    category: "Ethics",
    lastUpdated: "2023-12-20",
    version: "1.8",
    status: "Active",
    size: "956 KB",
    downloads: 289
  },
  {
    id: 4,
    title: "Leave and Time Off Policy",
    description: "Vacation, sick leave, and other time-off policies and procedures",
    category: "Benefits",
    lastUpdated: "2024-01-05",
    version: "2.0",
    status: "Active",
    size: "1.8 MB",
    downloads: 201
  },
  {
    id: 5,
    title: "Performance Review Guidelines",
    description: "Process and criteria for employee performance evaluations",
    category: "Performance",
    lastUpdated: "2023-11-30",
    version: "1.5",
    status: "Under Review",
    size: "1.1 MB",
    downloads: 98
  },
  {
    id: 6,
    title: "Data Privacy Policy",
    description: "How we collect, use, and protect employee personal information",
    category: "Privacy",
    lastUpdated: "2024-01-20",
    version: "3.0",
    status: "Active",
    size: "2.1 MB",
    downloads: 134
  }
];

const policyCategories = [
  { name: "General", count: 1, color: "bg-blue-100 text-blue-800" },
  { name: "Work Arrangements", count: 1, color: "bg-green-100 text-green-800" },
  { name: "Ethics", count: 1, color: "bg-purple-100 text-purple-800" },
  { name: "Benefits", count: 1, color: "bg-orange-100 text-orange-800" },
  { name: "Performance", count: 1, color: "bg-yellow-100 text-yellow-800" },
  { name: "Privacy", count: 1, color: "bg-red-100 text-red-800" }
];

export function Policies() {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Active': return <Badge variant="success">Active</Badge>;
      case 'Under Review': return <Badge variant="warning">Under Review</Badge>;
      case 'Draft': return <Badge variant="neutral">Draft</Badge>;
      default: return <Badge variant="neutral">{status}</Badge>;
    }
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">HR Policies</h1>
          <p className="text-gray-600">Access and manage company policies and procedures</p>
        </div>
        <Button className="flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          Add Policy
        </Button>
      </div>

      {/* Search and Filters */}
      <Card className="mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search policies..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <select className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            <option value="all">All Categories</option>
            {policyCategories.map(category => (
              <option key={category.name} value={category.name}>{category.name}</option>
            ))}
          </select>
          <select className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="under-review">Under Review</option>
            <option value="draft">Draft</option>
          </select>
        </div>
      </Card>

      {/* Policy Categories */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {policyCategories.map((category) => (
          <Card key={category.name} className="text-center cursor-pointer hover:shadow-md transition-shadow">
            <h3 className="font-medium text-gray-900 mb-1">{category.name}</h3>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${category.color}`}>
              {category.count} {category.count === 1 ? 'Policy' : 'Policies'}
            </span>
          </Card>
        ))}
      </div>

      {/* Policies List */}
      <div className="space-y-4">
        {policies.map((policy) => (
          <Card key={policy.id}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <div className="flex items-center space-x-3 mb-1">
                    <h3 className="text-lg font-semibold text-gray-900">{policy.title}</h3>
                    {getStatusBadge(policy.status)}
                    <span className="text-sm text-gray-500">v{policy.version}</span>
                  </div>
                  <p className="text-gray-700 mb-2">{policy.description}</p>
                  <div className="flex items-center space-x-6 text-sm text-gray-600">
                    <span className="flex items-center">
                      <Calendar className="w-4 h-4 mr-1" />
                      Updated {new Date(policy.lastUpdated).toLocaleDateString()}
                    </span>
                    <span className="flex items-center">
                      <Download className="w-4 h-4 mr-1" />
                      {policy.downloads} downloads
                    </span>
                    <span>{policy.size}</span>
                    <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs">
                      {policy.category}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm">
                  <Eye className="w-4 h-4 mr-1" />
                  View
                </Button>
                <Button variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-1" />
                  Download
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Recent Updates */}
      <Card className="mt-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Policy Updates</h3>
        <div className="space-y-3">
          {policies
            .sort((a, b) => new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime())
            .slice(0, 3)
            .map((policy) => (
              <div key={policy.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-medium text-gray-900">{policy.title}</p>
                    <p className="text-sm text-gray-600">
                      Updated to version {policy.version} on {new Date(policy.lastUpdated).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <Button variant="outline" size="sm">
                  View Changes
                </Button>
              </div>
            ))}
        </div>
      </Card>
    </div>
  );
}