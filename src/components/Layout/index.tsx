import { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import {
  AppBar,
  Box,
  CssBaseline,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Avatar,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Assignment as SurveyIcon,
  Assessment as AssessmentIcon,
  Analytics as AnalyticsIcon,
  Psychology as BrainIcon,
  BarChart as BarChartIcon,
  TrendingUp as TrendingUpIcon,
  Search as SearchIcon,
  Message as MessageIcon,
} from '@mui/icons-material';
import { RootState } from '../../store';
import { logout } from '../../store/slices/authSlice';

const drawerWidth = 240;

const navigationSections = [
  {
    title: 'Main',
    items: [
      { text: 'Overview', icon: <DashboardIcon />, path: '/' },
      { text: 'Employees', icon: <PeopleIcon />, path: '/employees' },
      { text: 'Focus Groups', icon: <PeopleIcon />, path: '/focus-groups' },
    ],
  },
  {
    title: 'Engagement',
    items: [
      { text: 'Surveys', icon: <SurveyIcon />, path: '/surveys' },
      { text: 'Enhanced Surveys', icon: <SurveyIcon />, path: '/enhanced-surveys' },
      { text: 'Questions', icon: <SurveyIcon />, path: '/questions' },
      { text: 'KPI Management', icon: <AnalyticsIcon />, path: '/kpis' },
    ],
  },
  {
    title: 'Performance',
    items: [
      { text: 'Performance', icon: <AssessmentIcon />, path: '/performance' },
      { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' },
      { text: 'Parameter Management', icon: <BrainIcon />, path: '/parameter-management' },
      { text: 'Advanced KPIs', icon: <BarChartIcon />, path: '/advanced-kpi-dashboard' },
      { text: 'Advanced Analytics', icon: <TrendingUpIcon />, path: '/advanced-analytics' },
    ],
  },
  {
    title: 'Improvement',
    items: [
      { text: 'Action Plans', icon: <AssessmentIcon />, path: '/action-plans' },
      { text: 'Initiatives', icon: <AssessmentIcon />, path: '/initiatives' },
    ],
  },
  {
    title: 'Support',
    items: [
      { text: 'Help Centre', icon: <DashboardIcon />, path: '/help' },
      { text: 'HR Policies', icon: <DashboardIcon />, path: '/policies' },
    ],
  },
];

export default function Layout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const { user } = useSelector((state: RootState) => state.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    dispatch(logout() as any);
    navigate('/login');
  };

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          HR Dashboard
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {navigationSections.map(section => (
          <div key={section.title}>
            <ListItem>
              <ListItemText primary={section.title.toUpperCase()} primaryTypographyProps={{ variant: 'caption', sx: { pl: 1, color: 'text.secondary' } }} />
            </ListItem>
            {section.items.map(item => (
              <ListItem key={item.text} disablePadding>
                <ListItemButton selected={window.location.pathname === item.path} onClick={() => navigate(item.path)}>
                  <ListItemIcon sx={{ color: 'inherit' }}>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            ))}
          </div>
        ))}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {navigationSections.find(section => section.items.some(item => item.path === window.location.pathname))?.title || 'Dashboard'}
          </Typography>
          <div>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
            >
              <Avatar sx={{ width: 32, height: 32 }}>
                {user?.email?.charAt(0).toUpperCase() || 'U'}
              </Avatar>
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={handleClose}>Profile</MenuItem>
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </Menu>
          </div>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: '64px',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
} 