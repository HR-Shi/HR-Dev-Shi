import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { dashboardAPI } from '../api';
import { FocusGroup } from '../types';
import { 
  GpsFixed as Target, 
  Add as Plus, 
  People as Users, 
  CalendarToday as Calendar, 
  Settings, 
  BarChart 
} from '@mui/icons-material';

export function FocusGroups() {
  const [focusGroups, setFocusGroups] = useState<FocusGroup[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFocusGroups = async () => {
      try {
        const data = await dashboardAPI.getFocusGroups();
        setFocusGroups(data);
      } catch (error) {
        console.error('Error fetching focus groups:', error);
        // Add some sample data for demo
        setFocusGroups([
          {
            id: '1',
            name: "Engineering Team Feedback",
            description: "Focus group for gathering engineering team insights on development processes",
            employee_count: 12,
            created_at: "2024-01-15",
            status: "active"
          },
          {
            id: '2',
            name: "Remote Work Experience",
            description: "Understanding remote work challenges and opportunities across departments",
            employee_count: 25,
            created_at: "2024-01-10",
            status: "active"
          },
          {
            id: '3',
            name: "New Hire Onboarding",
            description: "Feedback from recent hires on the onboarding experience",
            employee_count: 8,
            created_at: "2024-01-05",
            status: "completed"
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchFocusGroups();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active': return <Badge variant="success">Active</Badge>;
      case 'completed': return <Badge variant="neutral">Completed</Badge>;
      case 'draft': return <Badge variant="warning">Draft</Badge>;
      default: return <Badge variant="neutral">{status}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Focus Groups</h1>
          <p className="text-gray-600">Organize and analyze targeted employee feedback sessions</p>
        </div>
        <Button className="flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          Create Focus Group
        </Button>
      </div>

      {/* Focus Group Templates */}
      <Card className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Focus Group Templates</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
            <div className="flex items-center mb-2">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                <Target className="w-4 h-4 text-blue-600" />
              </div>
              <h4 className="font-medium text-gray-900">Department Feedback</h4>
            </div>
            <p className="text-sm text-gray-600">Gather insights from specific departments or teams</p>
          </div>
          <div className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
            <div className="flex items-center mb-2">
              <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                <Users className="w-4 h-4 text-green-600" />
              </div>
              <h4 className="font-medium text-gray-900">New Hire Group</h4>
            </div>
            <p className="text-sm text-gray-600">Focus on recent hires and onboarding experience</p>
          </div>
          <div className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
            <div className="flex items-center mb-2">
              <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                <BarChart className="w-4 h-4 text-purple-600" />
              </div>
              <h4 className="font-medium text-gray-900">Performance Review</h4>
            </div>
            <p className="text-sm text-gray-600">Discuss performance management and career development</p>
          </div>
        </div>
      </Card>

      {/* Focus Groups List */}
      <div className="space-y-4">
        {focusGroups.map((group) => (
          <Card key={group.id}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
                  <Target className="w-6 h-6 text-indigo-600" />
                </div>
                <div>
                  <div className="flex items-center space-x-3 mb-1">
                    <h3 className="text-lg font-semibold text-gray-900">{group.name}</h3>
                    {getStatusBadge(group.status)}
                  </div>
                  <p className="text-gray-700 mb-2">{group.description}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span className="flex items-center">
                      <Users className="w-4 h-4 mr-1" />
                      {group.employee_count} participants
                    </span>
                    <span className="flex items-center">
                      <Calendar className="w-4 h-4 mr-1" />
                      Created {new Date(group.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm">
                  <BarChart className="w-4 h-4 mr-1" />
                  View Insights
                </Button>
                <Button variant="outline" size="sm">
                  <Settings className="w-4 h-4 mr-1" />
                  Manage
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {focusGroups.length === 0 && (
        <Card className="text-center py-12">
          <Target className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No focus groups yet</h3>
          <p className="text-gray-600 mb-4">Create your first focus group to start gathering targeted feedback.</p>
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Create Your First Focus Group
          </Button>
        </Card>
      )}
    </div>
  );
}