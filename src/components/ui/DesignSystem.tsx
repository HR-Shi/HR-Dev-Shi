import React from 'react';
import { styled, createTheme, ThemeProvider } from '@mui/material/styles';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Button,
  Alert,
  LinearProgress,
  CircularProgress,
  Tooltip,
  Badge,
  Avatar
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Info,
  Warning,
  CheckCircle,
  Error,
  People,
  Assessment,
  Analytics,
  Star
} from '@mui/icons-material';

// =====================================================
// DESIGN SYSTEM THEME
// =====================================================

export const hrDashboardTheme = createTheme({
  palette: {
    primary: {
      main: '#2563eb', // Blue
      light: '#60a5fa',
      dark: '#1d4ed8',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#7c3aed', // Purple
      light: '#a78bfa',
      dark: '#5b21b6',
      contrastText: '#ffffff',
    },
    success: {
      main: '#10b981', // Green
      light: '#34d399',
      dark: '#059669',
    },
    warning: {
      main: '#f59e0b', // Amber
      light: '#fbbf24',
      dark: '#d97706',
    },
    error: {
      main: '#ef4444', // Red
      light: '#f87171',
      dark: '#dc2626',
    },
    info: {
      main: '#06b6d4', // Cyan
      light: '#22d3ee',
      dark: '#0891b2',
    },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
    },
    text: {
      primary: '#1e293b',
      secondary: '#64748b',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.25rem',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '1.875rem',
      fontWeight: 600,
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    caption: {
      fontSize: '0.75rem',
      lineHeight: 1.4,
      color: '#64748b',
    },
  },
  shape: {
    borderRadius: 8,
  },
  shadows: [
    'none',
    '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none',
    'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none',
  ],
});

// =====================================================
// STYLED COMPONENTS
// =====================================================

export const StyledCard = styled(Card)(({ theme }) => ({
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[1],
  border: '1px solid rgba(226, 232, 240, 0.8)',
  transition: 'all 0.2s ease-in-out',
  '&:hover': {
    boxShadow: theme.shadows[2],
    transform: 'translateY(-1px)',
  },
}));

export const GradientCard = styled(Card)(({ theme }) => ({
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  color: 'white',
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[3],
  '& .MuiCardContent-root': {
    '&:last-child': {
      paddingBottom: theme.spacing(2),
    },
  },
}));

export const StatusBadge = styled(Chip)<{ status: 'active' | 'pending' | 'completed' | 'overdue' }>(
  ({ theme, status }) => {
    const colors = {
      active: { bg: '#dcfce7', color: '#166534', border: '#bbf7d0' },
      pending: { bg: '#fef3c7', color: '#92400e', border: '#fde68a' },
      completed: { bg: '#dbeafe', color: '#1e40af', border: '#bfdbfe' },
      overdue: { bg: '#fee2e2', color: '#991b1b', border: '#fecaca' },
    };
    
    return {
      backgroundColor: colors[status].bg,
      color: colors[status].color,
      border: `1px solid ${colors[status].border}`,
      fontWeight: 500,
      fontSize: '0.75rem',
    };
  }
);

export const TrendIndicator = styled(Box)<{ trend: 'up' | 'down' | 'neutral' }>(
  ({ theme, trend }) => ({
    display: 'inline-flex',
    alignItems: 'center',
    padding: theme.spacing(0.5, 1),
    borderRadius: theme.shape.borderRadius,
    fontSize: '0.875rem',
    fontWeight: 500,
    backgroundColor: trend === 'up' ? '#dcfce7' : trend === 'down' ? '#fee2e2' : '#f1f5f9',
    color: trend === 'up' ? '#166534' : trend === 'down' ? '#991b1b' : '#475569',
  })
);

// =====================================================
// KPI CARD COMPONENT
// =====================================================

interface KPICardProps {
  title: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  loading?: boolean;
}

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  change,
  trend = 'neutral',
  icon,
  color = 'primary',
  loading = false,
}) => {
  const theme = hrDashboardTheme;
  
  return (
    <StyledCard>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
            {title}
          </Typography>
          {icon && (
            <Avatar
              sx={{
                bgcolor: theme.palette[color].main,
                width: 40,
                height: 40,
              }}
            >
              {icon}
            </Avatar>
          )}
        </Box>
        
        {loading ? (
          <Box display="flex" alignItems="center" mb={1}>
            <CircularProgress size={20} sx={{ mr: 1 }} />
            <Typography variant="body2" color="text.secondary">Loading...</Typography>
          </Box>
        ) : (
          <>
            <Typography variant="h3" component="div" sx={{ fontWeight: 700, mb: 1 }}>
              {value}
            </Typography>
            
            {change !== undefined && (
              <TrendIndicator trend={trend}>
                {trend === 'up' && <TrendingUp sx={{ fontSize: 16, mr: 0.5 }} />}
                {trend === 'down' && <TrendingDown sx={{ fontSize: 16, mr: 0.5 }} />}
                {Math.abs(change)}% from last period
              </TrendIndicator>
            )}
          </>
        )}
      </CardContent>
    </StyledCard>
  );
};

// =====================================================
// PROGRESS CARD COMPONENT
// =====================================================

interface ProgressCardProps {
  title: string;
  progress: number;
  description?: string;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  showValue?: boolean;
}

export const ProgressCard: React.FC<ProgressCardProps> = ({
  title,
  progress,
  description,
  color = 'primary',
  showValue = true,
}) => {
  return (
    <StyledCard>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
          {showValue && (
            <Typography variant="h6" color={`${color}.main`} sx={{ fontWeight: 700 }}>
              {progress}%
            </Typography>
          )}
        </Box>
        
        <LinearProgress
          variant="determinate"
          value={progress}
          color={color}
          sx={{
            height: 8,
            borderRadius: 4,
            mb: description ? 1 : 0,
          }}
        />
        
        {description && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {description}
          </Typography>
        )}
      </CardContent>
    </StyledCard>
  );
};

// =====================================================
// ALERT COMPONENTS
// =====================================================

interface SmartAlertProps {
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  action?: React.ReactNode;
  dismissible?: boolean;
  onDismiss?: () => void;
}

export const SmartAlert: React.FC<SmartAlertProps> = ({
  type,
  title,
  message,
  action,
  dismissible = false,
  onDismiss,
}) => {
  const icons = {
    info: <Info />,
    success: <CheckCircle />,
    warning: <Warning />,
    error: <Error />,
  };

  return (
    <Alert
      severity={type}
      icon={icons[type]}
      action={action}
      onClose={dismissible ? onDismiss : undefined}
      sx={{
        borderRadius: 2,
        '& .MuiAlert-message': {
          width: '100%',
        },
      }}
    >
      <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
        {title}
      </Typography>
      <Typography variant="body2">{message}</Typography>
    </Alert>
  );
};

// =====================================================
// INTERACTIVE TOOLTIP
// =====================================================

interface InteractiveTooltipProps {
  title: string;
  content: React.ReactNode;
  children: React.ReactElement;
  placement?: 'top' | 'bottom' | 'left' | 'right';
}

export const InteractiveTooltip: React.FC<InteractiveTooltipProps> = ({
  title,
  content,
  children,
  placement = 'top',
}) => {
  return (
    <Tooltip
      title={
        <Box sx={{ p: 1 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
            {title}
          </Typography>
          {content}
        </Box>
      }
      placement={placement}
      arrow
      componentsProps={{
        tooltip: {
          sx: {
            bgcolor: 'common.white',
            color: 'text.primary',
            boxShadow: 3,
            border: '1px solid rgba(0, 0, 0, 0.1)',
            borderRadius: 2,
            maxWidth: 300,
          },
        },
        arrow: {
          sx: {
            color: 'common.white',
            '&::before': {
              border: '1px solid rgba(0, 0, 0, 0.1)',
            },
          },
        },
      }}
    >
      {children}
    </Tooltip>
  );
};

// =====================================================
// SECTION HEADER COMPONENT
// =====================================================

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
  color?: string;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  subtitle,
  action,
  icon,
  color,
}) => {
  return (
    <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
      <Box display="flex" alignItems="center">
        {icon && (
          <Box
            sx={{
              mr: 2,
              p: 1,
              borderRadius: 2,
              bgcolor: color ? `${color}.100` : 'primary.100',
              color: color ? `${color}.600` : 'primary.600',
            }}
          >
            {icon}
          </Box>
        )}
        <Box>
          <Typography variant="h4" component="h2" sx={{ fontWeight: 700 }}>
            {title}
          </Typography>
          {subtitle && (
            <Typography variant="body1" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
      </Box>
      {action && <Box>{action}</Box>}
    </Box>
  );
};

// =====================================================
// COLOR SYSTEM
// =====================================================

export const ColorSystem = {
  // Module Colors
  modules: {
    employees: '#3b82f6', // Blue
    surveys: '#8b5cf6', // Purple
    kpis: '#10b981', // Green
    analytics: '#f59e0b', // Amber
    actionPlans: '#ef4444', // Red
    performance: '#06b6d4', // Cyan
    focusGroups: '#ec4899', // Pink
  },
  
  // Status Colors
  status: {
    active: '#10b981',
    inactive: '#6b7280',
    pending: '#f59e0b',
    completed: '#3b82f6',
    overdue: '#ef4444',
    cancelled: '#8b5cf6',
  },
  
  // Sentiment Colors
  sentiment: {
    positive: '#10b981',
    neutral: '#6b7280',
    negative: '#ef4444',
    mixed: '#f59e0b',
  },
  
  // Priority Colors
  priority: {
    low: '#10b981',
    medium: '#f59e0b',
    high: '#ef4444',
    critical: '#7c2d12',
  },
};

// =====================================================
// ACCESSIBILITY HELPERS
// =====================================================

export const AccessibilityHelpers = {
  // Screen reader only text
  srOnly: {
    position: 'absolute',
    width: '1px',
    height: '1px',
    padding: 0,
    margin: '-1px',
    overflow: 'hidden',
    clip: 'rect(0, 0, 0, 0)',
    whiteSpace: 'nowrap',
    border: 0,
  } as React.CSSProperties,
  
  // Focus visible styles
  focusVisible: {
    '&:focus-visible': {
      outline: '2px solid #2563eb',
      outlineOffset: '2px',
      borderRadius: '4px',
    },
  },
  
  // High contrast mode support
  highContrast: {
    '@media (prefers-contrast: high)': {
      borderWidth: '2px',
      borderStyle: 'solid',
    },
  },
};

// =====================================================
// ANIMATION SYSTEM
// =====================================================

export const AnimationSystem = {
  // Entrance animations
  fadeIn: {
    '@keyframes fadeIn': {
      '0%': { opacity: 0, transform: 'translateY(10px)' },
      '100%': { opacity: 1, transform: 'translateY(0)' },
    },
    animation: 'fadeIn 0.3s ease-out',
  },
  
  // Loading states
  pulse: {
    '@keyframes pulse': {
      '0%': { opacity: 1 },
      '50%': { opacity: 0.5 },
      '100%': { opacity: 1 },
    },
    animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
  },
  
  // Micro-interactions
  scaleOnHover: {
    transition: 'transform 0.2s ease-in-out',
    '&:hover': {
      transform: 'scale(1.02)',
    },
  },
};

export default {
  hrDashboardTheme,
  StyledCard,
  GradientCard,
  StatusBadge,
  TrendIndicator,
  KPICard,
  ProgressCard,
  SmartAlert,
  InteractiveTooltip,
  SectionHeader,
  ColorSystem,
  AccessibilityHelpers,
  AnimationSystem,
}; 