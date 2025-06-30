import { NavLink } from 'react-router-dom';
import { 
  Dashboard, 
  People, 
  Flag, 
  BarChart, 
  MessageOutlined, 
  CheckBox, 
  TrendingUp, 
  HelpOutline, 
  DescriptionOutlined,
  PersonOutlined
} from '@mui/icons-material';

const navigation = [
  {
    section: 'Main',
    color: 'text-blue-600',
    items: [
      { name: 'Overview', href: '/', icon: Dashboard },
      { name: 'Employees', href: '/employees', icon: People },
      { name: 'Focus Groups', href: '/focus-groups', icon: Flag },
    ],
  },
  {
    section: 'Engagement',
    color: 'text-teal-600',
    items: [
      { name: 'Surveys', href: '/surveys', icon: BarChart },
      { name: 'Questions', href: '/questions', icon: MessageOutlined },
      { name: 'KPI Management', href: '/kpis', icon: TrendingUp },
    ],
  },
  {
    section: 'Improvement',
    color: 'text-orange-600',
    items: [
      { name: 'Action Plans', href: '/action-plans', icon: CheckBox },
      { name: 'Initiatives', href: '/initiatives', icon: TrendingUp },
    ],
  },
  {
    section: 'Support',
    color: 'text-gray-600',
    items: [
      { name: 'Help Centre', href: '/help', icon: HelpOutline },
      { name: 'HR Policies', href: '/policies', icon: DescriptionOutlined },
    ],
  },
];

export function Sidebar() {
  return (
    <div className="flex flex-col w-64 bg-white shadow-lg">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-gray-900">HR Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Business Intelligence</p>
      </div>
      
      <nav className="flex-1 px-4 pb-4">
        {navigation.map((section) => (
          <div key={section.section} className="mb-6">
            <h3 className={`text-xs font-semibold uppercase tracking-wider ${section.color} mb-3`}>
              {section.section}
            </h3>
            <ul className="space-y-1">
              {section.items.map((item) => (
                <li key={item.name}>
                  <NavLink
                    to={item.href}
                    className={({ isActive }) =>
                      `group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                        isActive
                          ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                          : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                      }`
                    }
                  >
                    <item.icon className="w-5 h-5 mr-3" />
                    {item.name}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
      
      <div className="border-t border-gray-200 p-4">
        <div className="flex items-center">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <PersonOutlined className="w-4 h-4 text-white" />
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium text-gray-700">HR Admin</p>
            <p className="text-xs text-gray-500">People Team</p>
          </div>
        </div>
      </div>
    </div>
  );
}