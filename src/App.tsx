import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { useSelector, useDispatch } from 'react-redux';
import { useEffect } from 'react';
import { RootState, AppDispatch } from './store';
import { setUser, restoreSession } from './store/slices/authSlice';

// Layout
import Layout from './components/Layout';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Employees from './pages/Employees';
import Surveys from './pages/Surveys';
import Performance from './pages/Performance';
import Analytics from './pages/Analytics';
import { FocusGroups } from './pages/FocusGroups';
import { Questions } from './pages/Questions';
import { KPIs } from './pages/KPIs';
import { ActionPlans } from './pages/ActionPlans';
import { Initiatives } from './pages/Initiatives';
import { Help } from './pages/Help';
import { Policies } from './pages/Policies';
import { AIDemo } from './pages/AIDemo';
import { OutlierDetection } from './pages/OutlierDetection';
import { EnhancedSurveySystem } from './pages/EnhancedSurveySystem';
import { PerformanceManagement } from './pages/PerformanceManagement';
import ParameterManagement from './pages/ParameterManagement';
import AdvancedKPIDashboard from './pages/AdvancedKPIDashboard';
import { AdvancedAnalytics } from './pages/AdvancedAnalytics';

// Create theme
import { theme } from './theme';

// Protected Route component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user } = useSelector((state: RootState) => state.auth);
  const token = localStorage.getItem('access_token');
  const savedUser = localStorage.getItem('current_user');
  
  console.log('ProtectedRoute - user from store:', user);
  console.log('ProtectedRoute - token:', !!token);
  console.log('ProtectedRoute - savedUser:', !!savedUser);
  
  // Allow access if we have user in store, or if we have valid session data
  const hasValidSession = user || (token && savedUser);
  
  return hasValidSession ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
  console.log('App component rendering');
  const dispatch = useDispatch<AppDispatch>();
  
  useEffect(() => {
    // Restore user session from localStorage
    dispatch(restoreSession());
  }, [dispatch]);
  
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="employees" element={<Employees />} />
            <Route path="surveys" element={<Surveys />} />
            <Route path="questions" element={<Questions />} />
            <Route path="kpis" element={<KPIs />} />
            <Route path="focus-groups" element={<FocusGroups />} />
            <Route path="action-plans" element={<ActionPlans />} />
            <Route path="initiatives" element={<Initiatives />} />
            <Route path="help" element={<Help />} />
            <Route path="policies" element={<Policies />} />
            <Route path="ai-demo" element={<AIDemo />} />
            <Route path="outlier-detection" element={<OutlierDetection />} />
            <Route path="enhanced-surveys" element={<EnhancedSurveySystem />} />
            <Route path="performance-management" element={<PerformanceManagement />} />
            <Route path="parameter-management" element={<ParameterManagement />} />
            <Route path="advanced-kpi-dashboard" element={<AdvancedKPIDashboard />} />
            <Route path="advanced-analytics" element={<AdvancedAnalytics />} />
            <Route path="performance" element={<Performance />} />
            <Route path="analytics" element={<Analytics />} />
          </Route>
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;