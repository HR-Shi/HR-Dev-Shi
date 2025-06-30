import React from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { 
  ChatBubbleOutline as MessageSquare, 
  Add as Plus, 
  Settings, 
  Star, 
  BarChart 
} from '@mui/icons-material';

const questionCategories = [
  {
    name: 'Engagement',
    count: 12,
    color: 'bg-blue-100 text-blue-800',
    questions: [
      'How satisfied are you with your current role?',
      'Do you feel valued by your immediate supervisor?',
      'Would you recommend this company as a great place to work?'
    ]
  },
  {
    name: 'Work-Life Balance',
    count: 8,
    color: 'bg-green-100 text-green-800',
    questions: [
      'How well are you able to balance your work and personal life?',
      'Do you feel you have adequate time for personal activities?',
      'Are you satisfied with your current workload?'
    ]
  },
  {
    name: 'Development',
    count: 10,
    color: 'bg-purple-100 text-purple-800',
    questions: [
      'Do you have opportunities for professional growth?',
      'Are you satisfied with the training and development opportunities?',
      'Do you feel your skills are being utilized effectively?'
    ]
  },
  {
    name: 'Communication',
    count: 6,
    color: 'bg-orange-100 text-orange-800',
    questions: [
      'How effective is communication within your team?',
      'Do you receive regular feedback from your supervisor?',
      'Are company goals and expectations clearly communicated?'
    ]
  }
];

export function Questions() {
  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Question Bank</h1>
          <p className="text-gray-600">Manage and organize survey questions for your assessments</p>
        </div>
        <Button className="flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          Add Question
        </Button>
      </div>

      {/* Question Categories */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {questionCategories.map((category) => (
          <Card key={category.name} className="text-center">
            <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <MessageSquare className="w-6 h-6 text-teal-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{category.name}</h3>
            <p className="text-2xl font-bold text-gray-900 mb-2">{category.count}</p>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${category.color}`}>
              Questions Available
            </span>
          </Card>
        ))}
      </div>

      {/* Most Used Questions */}
      <Card className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Most Used Questions</h3>
          <Badge variant="info">Top Rated</Badge>
        </div>
        <div className="space-y-3">
          {[
            { question: "How satisfied are you with your current role?", category: "Engagement", usage: 95 },
            { question: "Would you recommend this company as a great place to work?", category: "Engagement", usage: 87 },
            { question: "Do you feel valued by your immediate supervisor?", category: "Engagement", usage: 82 },
            { question: "How well are you able to balance your work and personal life?", category: "Work-Life Balance", usage: 78 },
          ].map((item, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <Star className="w-5 h-5 text-yellow-500" />
                <div>
                  <p className="font-medium text-gray-900">{item.question}</p>
                  <p className="text-sm text-gray-600">{item.category}</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-center">
                  <p className="text-sm font-semibold text-gray-900">{item.usage}%</p>
                  <p className="text-xs text-gray-600">Usage Rate</p>
                </div>
                <Button variant="outline" size="sm">
                  <Settings className="w-4 h-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Question Categories Detail */}
      <div className="space-y-6">
        {questionCategories.map((category) => (
          <Card key={category.name}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <h3 className="text-lg font-semibold text-gray-900">{category.name} Questions</h3>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${category.color}`}>
                  {category.count} Questions
                </span>
              </div>
              <Button variant="outline" size="sm">
                <Plus className="w-4 h-4 mr-1" />
                Add Question
              </Button>
            </div>
            
            <div className="space-y-3">
              {category.questions.map((question, index) => (
                <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                  <p className="text-gray-900">{question}</p>
                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm">
                      <BarChart className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Settings className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}