import { createTheme } from '@material-ui/core';

/**
 * Theme Defaults: https://mui.com/material-ui/customization/theming
 */
export const darkTheme = createTheme({
  palette: {
    // Yellow
    primary: {
      main: '#F4E346',
      light: '#F8ED87',
      dark: '#F1DA0E',
      contrastText: '#121212',
    },

    // Green
    secondary: {
      main: '#13D491',
      light: '#14EBA0',
      dark: '#10BC80',
      contrastText: '#121212',
    },

    // Blue
    tertiary: {
      main: '#01A6F7',
      light: '#1BB2FE',
      dark: '#0188CB',
      contrastText: '#FFFFFF',
    },

    // Red
    error: {
      main: "#E03C6C",
    },

    // Black
    background: {
      main: '#121212',
      light: '#363636',
      contrastText: '#FFFFFF',
    }
  },
  typography: {
    fontFamily: [
      'DM Sans',
      'sans-serif',
    ].join(','),
  },
  header: {
    height: 66,
    marginBottom: 28,
    // Medium breakpoint.
    md: {
      height: 110,
      marginBottom: 86,
    }
  },
  footer: {
    height: 70,
  }
});
