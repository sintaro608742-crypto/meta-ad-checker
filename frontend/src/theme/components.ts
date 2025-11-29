import type { Components, Theme } from '@mui/material/styles';

export const components: Components<Theme> = {
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        padding: '10px 24px',
        fontSize: '0.875rem',
        fontWeight: 600,
        boxShadow: 'none',
        '&:hover': {
          boxShadow: '0 4px 12px rgba(16, 185, 129, 0.2)',
        },
      },
      contained: {
        '&:hover': {
          boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
        },
      },
      sizeLarge: {
        padding: '12px 32px',
        fontSize: '1rem',
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 12,
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
        '&:hover': {
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.12)',
        },
      },
    },
  },
  MuiPaper: {
    styleOverrides: {
      root: {
        borderRadius: 12,
      },
      elevation1: {
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      },
      elevation2: {
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
      },
      elevation3: {
        boxShadow: '0 6px 16px rgba(0, 0, 0, 0.12)',
      },
    },
  },
  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: 8,
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: '#10b981',
          },
        },
      },
    },
  },
  MuiAppBar: {
    styleOverrides: {
      root: {
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      },
    },
  },
  MuiChip: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        fontWeight: 600,
      },
    },
  },
  MuiAlert: {
    styleOverrides: {
      root: {
        borderRadius: 8,
      },
      standardSuccess: {
        backgroundColor: '#d1fae5',
        color: '#065f46',
      },
      standardError: {
        backgroundColor: '#fee2e2',
        color: '#991b1b',
      },
      standardWarning: {
        backgroundColor: '#fef3c7',
        color: '#92400e',
      },
      standardInfo: {
        backgroundColor: '#cffafe',
        color: '#164e63',
      },
    },
  },
};
