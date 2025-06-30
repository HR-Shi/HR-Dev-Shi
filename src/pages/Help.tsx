import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { 
  HelpOutline, 
  MenuBook, 
  ChatBubbleOutline, 
  VideoLibrary, 
  Description, 
  Search, 
  Email, 
  Phone 
} from '@mui/icons-material';

const helpCategories = [
  {
    title: "Getting Started",
    icon: MenuBook,
    color: "bg-blue-100 text-blue-600",
    articles: [
      "Setting up your first survey",
      "Understanding KPI metrics",
      "Creating employee profiles",
      "Dashboard navigation guide"
    ]
  },
  {
    title: "Surveys & Feedback",
    icon: ChatBubbleOutline,
    color: "bg-green-100 text-green-600",
    articles: [
      "Creating pulse surveys",
      "Platform integrations (Slack, Teams)",
      "Analyzing survey results",
      "Best practices for question design"
    ]
  },
  {
    title: "Analytics & Reporting",
    icon: Description,
    color: "bg-purple-100 text-purple-600",
    articles: [
      "Understanding engagement metrics",
      "Outlier detection explained",
      "Exporting reports and data",
      "Setting up automated alerts"
    ]
  },
  {
    title: "Action Plans",
    icon: HelpOutline,
    color: "bg-orange-100 text-orange-600",
    articles: [
      "AI-generated action plans",
      "Measuring plan effectiveness",
      "Assigning plans to employees",
      "Tracking progress and outcomes"
    ]
  }
];

const faqs = [
  {
    question: "How often should I run employee surveys?",
    answer: "We recommend running pulse surveys weekly or bi-weekly, with comprehensive engagement surveys quarterly. The frequency depends on your organization's size and needs."
  },
  {
    question: "What is an outlier in employee data?",
    answer: "Outliers are employees whose engagement scores, performance metrics, or survey responses significantly deviate from the norm, indicating they may need additional support or attention."
  },
  {
    question: "How does the AI action plan generation work?",
    answer: "Our AI analyzes your KPI data, survey responses, and industry best practices to suggest targeted action plans that address specific issues identified in your workforce."
  },
  {
    question: "Can I integrate with Slack and Microsoft Teams?",
    answer: "Yes! Our platform supports seamless integration with popular collaboration tools to deploy surveys and collect feedback directly within your team's workflow."
  },
  {
    question: "How do I measure the success of action plans?",
    answer: "Action plan efficacy is measured through follow-up surveys and KPI tracking. The system automatically calculates improvement percentages based on pre and post-implementation data."
  }
];

export function Help() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Help Center</h1>
        <p className="text-gray-600">Find answers, guides, and resources to get the most out of your HR Dashboard</p>
      </div>

      {/* Search */}
      <Card className="mb-8">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search help articles, guides, and FAQs..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <Button>Search</Button>
        </div>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card className="text-center hover:shadow-md transition-shadow cursor-pointer">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <VideoLibrary className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Video Tutorials</h3>
          <p className="text-gray-600">Watch step-by-step guides for all features</p>
        </Card>
        
        <Card className="text-center hover:shadow-md transition-shadow cursor-pointer">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <ChatBubbleOutline className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Live Chat</h3>
          <p className="text-gray-600">Get instant help from our support team</p>
        </Card>
        
        <Card className="text-center hover:shadow-md transition-shadow cursor-pointer">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <MenuBook className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Documentation</h3>
          <p className="text-gray-600">Comprehensive guides and API references</p>
        </Card>
      </div>

      {/* Help Categories */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {helpCategories.map((category) => {
          const Icon = category.icon;
          return (
            <Card key={category.title}>
              <div className="flex items-center mb-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center mr-3 ${category.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">{category.title}</h3>
              </div>
              <ul className="space-y-2">
                {category.articles.map((article, index) => (
                  <li key={index}>
                    <a 
                      href="#" 
                      className="text-blue-600 hover:text-blue-800 hover:underline"
                    >
                      {article}
                    </a>
                  </li>
                ))}
              </ul>
            </Card>
          );
        })}
      </div>

      {/* FAQs */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Frequently Asked Questions</h3>
        <div className="space-y-6">
          {faqs.map((faq, index) => (
            <div key={index} className="border-b border-gray-200 pb-4 last:border-b-0">
              <h4 className="text-medium font-semibold text-gray-900 mb-2">{faq.question}</h4>
              <p className="text-gray-700">{faq.answer}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Contact Support */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <div className="flex items-center mb-3">
            <Email className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Email Support</h3>
          </div>
          <p className="text-gray-600 mb-4">Get detailed help via email within 24 hours</p>
          <Button variant="outline" className="w-full">
            support@hrdashboard.com
          </Button>
        </Card>
        
        <Card>
          <div className="flex items-center mb-3">
            <Phone className="w-5 h-5 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Phone Support</h3>
          </div>
          <p className="text-gray-600 mb-4">Speak with our support team directly</p>
          <Button variant="outline" className="w-full">
            +1 (555) 123-4567
          </Button>
        </Card>
      </div>
    </div>
  );
}