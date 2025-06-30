import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { 
  TrendingUp, 
  Add, 
  CalendarToday, 
  People, 
  Flag, 
  CheckCircle, 
  Schedule, 
  Warning 
} from '@mui/icons-material';

const initiatives = [
  {
    id: 1,
    title: "Diversity & Inclusion Program",
    description: "Company-wide initiative to improve diversity hiring and create inclusive workplace culture",
    status: "in-progress",
    progress: 65,
    startDate: "2024-01-01",
    endDate: "2024-06-30",
    owner: "Sarah Johnson",
    participants: 120,
    category: "Culture",
    kpis: ["Diversity Metrics", "Employee Satisfaction Score"]
  },
  {
    id: 2,
    title: "Remote Work Optimization",
    description: "Enhance remote work tools and processes to improve productivity and collaboration",
    status: "completed",
    progress: 100,
    startDate: "2023-10-01",
    endDate: "2024-01-15",
    owner: "Michael Chen",
    participants: 85,
    category: "Technology",
    kpis: ["Employee Engagement Score", "Productivity Metrics"]
  },
  {
    id: 3,
    title: "Leadership Development Track",
    description: "Comprehensive program to develop next-generation leaders within the organization",
    status: "planning",
    progress: 20,
    startDate: "2024-03-01",
    endDate: "2024-12-31",
    owner: "Emily Rodriguez",
    participants: 25,
    category: "Development",
    kpis: ["Training Effectiveness", "Internal Promotion Rate"]
  },
  {
    id: 4,
    title: "Employee Wellness Program",
    description: "Mental health and wellness initiatives to support employee well-being",
    status: "in-progress",
    progress: 40,
    startDate: "2024-01-15",
    endDate: "2024-08-30",
    owner: "David Thompson",
    participants: 200,
    category: "Wellness",
    kpis: ["Employee Satisfaction Score", "Stress Levels"]
  }
];

export function Initiatives() {
  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'completed':
        return { badge: <Badge variant="success">Completed</Badge>, icon: CheckCircle, color: 'text-green-600' };
      case 'in-progress':
        return { badge: <Badge variant="info">In Progress</Badge>, icon: Schedule, color: 'text-blue-600' };
      case 'planning':
        return { badge: <Badge variant="warning">Planning</Badge>, icon: Warning, color: 'text-yellow-600' };
      default:
        return { badge: <Badge variant="neutral">Unknown</Badge>, icon: Schedule, color: 'text-gray-600' };
    }
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      'Culture': 'bg-purple-100 text-purple-800',
      'Technology': 'bg-blue-100 text-blue-800',
      'Development': 'bg-green-100 text-green-800',
      'Wellness': 'bg-pink-100 text-pink-800',
    };
    return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Strategic Initiatives</h1>
          <p className="text-gray-600">Track and manage company-wide improvement initiatives</p>
        </div>
        <Button className="flex items-center">
          <Add className="w-4 h-4 mr-2" />
          Create Initiative
        </Button>
      </div>

      {/* Initiative Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="text-center">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <TrendingUp className="w-6 h-6 text-blue-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">{initiatives.length}</p>
          <p className="text-sm text-gray-600">Total Initiatives</p>
        </Card>
        
        <Card className="text-center">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <CheckCircle className="w-6 h-6 text-green-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {initiatives.filter(i => i.status === 'completed').length}
          </p>
          <p className="text-sm text-gray-600">Completed</p>
        </Card>
        
        <Card className="text-center">
          <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <Schedule className="w-6 h-6 text-yellow-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {initiatives.filter(i => i.status === 'in-progress').length}
          </p>
          <p className="text-sm text-gray-600">In Progress</p>
        </Card>
        
        <Card className="text-center">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <People className="w-6 h-6 text-purple-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {initiatives.reduce((total, initiative) => total + initiative.participants, 0)}
          </p>
          <p className="text-sm text-gray-600">Total Participants</p>
        </Card>
      </div>

      {/* Initiatives List */}
      <div className="space-y-6">
        {initiatives.map((initiative) => {
          const statusInfo = getStatusInfo(initiative.status);
          const StatusIcon = statusInfo.icon;
          
          return (
            <Card key={initiative.id}>
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
                    <StatusIcon className={`w-6 h-6 ${statusInfo.color}`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-xl font-semibold text-gray-900">{initiative.title}</h3>
                      {statusInfo.badge}
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(initiative.category)}`}>
                        {initiative.category}
                      </span>
                    </div>
                    <p className="text-gray-700 mb-3">{initiative.description}</p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                      <div className="flex items-center">
                        <CalendarToday className="w-4 h-4 mr-1" />
                        <span>{new Date(initiative.startDate).toLocaleDateString()} - {new Date(initiative.endDate).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center">
                        <People className="w-4 h-4 mr-1" />
                        <span>{initiative.participants} participants</span>
                      </div>
                      <div className="flex items-center">
                        <Flag className="w-4 h-4 mr-1" />
                        <span>Owner: {initiative.owner}</span>
                      </div>
                      <div className="flex items-center">
                        <TrendingUp className="w-4 h-4 mr-1" />
                        <span>{initiative.progress}% complete</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <Button variant="outline">
                  View Details
                </Button>
              </div>
              
              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium text-gray-700">Progress</span>
                  <span className="text-sm text-gray-600">{initiative.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${initiative.progress}%` }}
                  ></div>
                </div>
              </div>
              
              {/* Associated KPIs */}
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Associated KPIs:</p>
                <div className="flex flex-wrap gap-2">
                  {initiative.kpis.map((kpi) => (
                    <Badge key={kpi} variant="neutral" size="sm">
                      {kpi}
                    </Badge>
                  ))}
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}