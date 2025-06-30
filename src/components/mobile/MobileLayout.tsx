import React, { useState, useEffect } from 'react';
import { useMediaQuery, useTheme } from '@mui/material';
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Box,
  Fab,
  Badge,
  Chip,
  SwipeableDrawer,
  BottomNavigation,
  BottomNavigationAction,
  useScrollTrigger,
  Slide,
  Divider,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  People,
  Assessment,
  Analytics,
  Notifications,
  Settings,
  Add,
  Close,
  Home,
  Work,
  Person,
  InsertChart,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

interface MobileLayoutProps {
  children: React.ReactNode;
}

interface HideOnScrollProps {
  children: React.ReactElement;
}

function HideOnScroll({ children }: HideOnScrollProps) {
  const trigger = useScrollTrigger();
  
  return (
    <Slide appear={false} direction="down" in={!trigger}>
      {children}
    </Slide>
  );
}

const MobileLayout: React.FC<MobileLayoutProps> = ({ children }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [fabOpen, setFabOpen] = useState(false);
  const [bottomNavValue, setBottomNavValue] = useState(0);
  
  const { user } = useSelector((state: RootState) => state.auth);

  // Mobile navigation items
  const navigationItems = [
    { text: 'Overview', icon: <Dashboard />, path: '/', value: 0 },
    { text: 'Employees', icon: <People />, path: '/employees', value: 1 },
    { text: 'Analytics', icon: <Analytics />, path: '/analytics', value: 2 },
    { text: 'Performance', icon: <Assessment />, path: '/performance', value: 3 },
  ];

  // Extended navigation for drawer
  const drawerItems = [
    { text: 'Overview', icon: <Dashboard />, path: '/' },
    { text: 'Employees', icon: <People />, path: '/employees' },
    { text: 'Focus Groups', icon: <People />, path: '/focus-groups' },
    { text: 'Surveys', icon: <Assessment />, path: '/surveys' },
    { text: 'KPI Management', icon: <Analytics />, path: '/kpis' },
    { text: 'Action Plans', icon: <Assessment />, path: '/action-plans' },
    { text: 'Performance', icon: <Work />, path: '/performance' },
    { text: 'Analytics', icon: <InsertChart />, path: '/analytics' },
    { text: 'Settings', icon: <Settings />, path: '/settings' },
  ];

  // FAB quick actions
  const fabActions = [
    { icon: <Assessment />, label: 'New Survey', action: () => navigate('/surveys?create=true') },
    { icon: <People />, label: 'Add Employee', action: () => navigate('/employees?create=true') },
    { icon: <Analytics />, label: 'Quick Report', action: () => navigate('/analytics?quick=true') },
  ];

  // Update bottom navigation based on current route
  useEffect(() => {
    const currentItem = navigationItems.find(item => item.path === location.pathname);
    if (currentItem) {
      setBottomNavValue(currentItem.value);
    }
  }, [location.pathname]);

  // Handle offline functionality
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    setDrawerOpen(false);
  };

  const handleBottomNavChange = (event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const item = navigationItems.find(item => item.value === newValue);
    if (item) {
      navigate(item.path);
    }
  };

  if (!isMobile) {
    return <>{children}</>;
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Mobile App Bar */}
      <HideOnScroll>
        <AppBar position="fixed" color="primary" elevation={0}>
          <Toolbar sx={{ minHeight: '56px !important' }}>
            <IconButton
              edge="start"
              color="inherit"
              aria-label="menu"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            
            <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontSize: '1.1rem' }}>
              HR Dashboard
            </Typography>

            {/* Offline indicator */}
            {!isOnline && (
              <Chip 
                label="Offline" 
                size="small" 
                color="warning" 
                sx={{ mr: 1, fontSize: '0.75rem' }} 
              />
            )}

            {/* Notifications */}
            <IconButton color="inherit" size="large">
              <Badge badgeContent={3} color="error">
                <Notifications />
              </Badge>
            </IconButton>
          </Toolbar>
        </AppBar>
      </HideOnScroll>

      {/* Mobile Navigation Drawer */}
      <SwipeableDrawer
        anchor="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onOpen={() => setDrawerOpen(true)}
        disableSwipeToOpen={false}
        ModalProps={{
          keepMounted: true, // Better mobile performance
        }}
        sx={{
          '& .MuiDrawer-paper': {
            width: 280,
            backgroundImage: 'linear-gradient(180deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
          },
        }}
      >
        <Box sx={{ overflow: 'auto' }}>
          {/* User Profile Section */}
          <Box sx={{ p: 2, textAlign: 'center', borderBottom: '1px solid rgba(255,255,255,0.2)' }}>
            <Box
              sx={{
                width: 60,
                height: 60,
                borderRadius: '50%',
                bgcolor: 'rgba(255,255,255,0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 8px',
                fontSize: '1.5rem',
                fontWeight: 'bold',
              }}
            >
              {user?.email?.charAt(0).toUpperCase()}
            </Box>
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              {user?.email}
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8, textTransform: 'capitalize' }}>
              {user?.role?.replace('_', ' ')}
            </Typography>
          </Box>

          {/* Navigation Items */}
          <List sx={{ pt: 1 }}>
            {drawerItems.map((item, index) => (
              <ListItem key={item.text} disablePadding>
                <ListItemButton
                  onClick={() => handleNavigation(item.path)}
                  selected={location.pathname === item.path}
                  sx={{
                    minHeight: 48,
                    '&.Mui-selected': {
                      bgcolor: 'rgba(255,255,255,0.2)',
                      '&:hover': {
                        bgcolor: 'rgba(255,255,255,0.3)',
                      },
                    },
                    '&:hover': {
                      bgcolor: 'rgba(255,255,255,0.1)',
                    },
                  }}
                >
                  <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText 
                    primary={item.text} 
                    primaryTypographyProps={{ fontSize: '0.95rem' }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>

          <Divider sx={{ mx: 2, my: 1, borderColor: 'rgba(255,255,255,0.2)' }} />

          {/* Quick Stats */}
          <Box sx={{ p: 2 }}>
            <Typography variant="caption" sx={{ opacity: 0.8, mb: 1, display: 'block' }}>
              Quick Stats
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              <Chip 
                label="85% Engagement" 
                size="small" 
                sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontSize: '0.75rem' }}
              />
              <Chip 
                label="12 Active Surveys" 
                size="small" 
                sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontSize: '0.75rem' }}
              />
            </Box>
          </Box>
        </Box>
      </SwipeableDrawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          pt: '56px', // App bar height
          pb: '56px', // Bottom navigation height
          overflow: 'auto',
          bgcolor: 'background.default',
        }}
      >
        {children}
      </Box>

      {/* Floating Action Button */}
      <Box sx={{ position: 'fixed', bottom: 70, right: 16, zIndex: 1000 }}>
        {fabOpen && (
          <Box sx={{ mb: 1 }}>
            {fabActions.map((action, index) => (
              <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography
                  variant="body2"
                  sx={{
                    mr: 1,
                    bgcolor: 'rgba(0,0,0,0.8)',
                    color: 'white',
                    px: 1,
                    py: 0.5,
                    borderRadius: 1,
                    fontSize: '0.75rem',
                  }}
                >
                  {action.label}
                </Typography>
                <Fab
                  size="small"
                  color="secondary"
                  onClick={action.action}
                  sx={{ mb: 0.5 }}
                >
                  {action.icon}
                </Fab>
              </Box>
            ))}
          </Box>
        )}
        <Fab
          color="primary"
          onClick={() => setFabOpen(!fabOpen)}
          sx={{
            transform: fabOpen ? 'rotate(45deg)' : 'rotate(0deg)',
            transition: 'transform 0.3s ease',
          }}
        >
          {fabOpen ? <Close /> : <Add />}
        </Fab>
      </Box>

      {/* Bottom Navigation */}
      <Box sx={{ position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 1000 }}>
        <BottomNavigation
          value={bottomNavValue}
          onChange={handleBottomNavChange}
          sx={{
            height: 56,
            bgcolor: 'background.paper',
            borderTop: '1px solid',
            borderColor: 'divider',
            '& .MuiBottomNavigationAction-root': {
              minWidth: 'auto',
              fontSize: '0.75rem',
            },
          }}
        >
          {navigationItems.map((item) => (
            <BottomNavigationAction
              key={item.value}
              label={item.text}
              icon={item.icon}
              sx={{
                '&.Mui-selected': {
                  color: 'primary.main',
                },
              }}
            />
          ))}
        </BottomNavigation>
      </Box>
    </Box>
  );
};

export default MobileLayout; 