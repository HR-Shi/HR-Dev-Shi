import { createTheme } from '@mui/material/styles';

// Premium "Ascot" theme – deep navy primary, soft plum secondary, elegant typography
export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1b2a4e', // Deep navy
      light: '#35446e',
      dark: '#0d1834',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#a64ac9', // Soft plum
      light: '#bf6ed6',
      dark: '#6f2190',
      contrastText: '#ffffff',
    },
    background: {
      default: '#f3f6fa',
      paper: '#ffffff',
    },
    success: {
      main: '#34a853',
    },
    warning: {
      main: '#f9ab00',
    },
    error: {
      main: '#d93025',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.6rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2.2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.8rem',
      fontWeight: 600,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        rounded: {
          borderRadius: 12,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        colorPrimary: {
          backgroundColor: '#ffffff',
          color: '#1b2a4e',
          boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#1b2a4e',
          color: '#ffffff',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          '&.Mui-selected': {
            backgroundColor: 'rgba(255,255,255,0.12)',
          },
          '&:hover': {
            backgroundColor: 'rgba(255,255,255,0.08)',
          },
        },
      },
    },
  },
}); 