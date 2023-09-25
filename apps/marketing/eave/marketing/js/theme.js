import { createTheme } from '@material-ui/core';

/**
 * Theme Defaults: https://mui.com/material-ui/customization/theming
 */
export const theme = createTheme({
  palette: {
    primary: {  // yellow
      main: '#F4E346',
      light: '#F8ED87',
      dark: '#F1DA0E',
      contrastText: '#121212',
    },
    secondary: {  // green
      main: '#13D491',
      light: '#14EBA0',
      dark: '#10BC80',
      contrastText: '#121212',
    },
    tertiary: {  // blue
      main: '#01A6F7',
      light: '#1BB2FE',
      dark: '#0188CB',
      contrastText: '#FFFFFF',
    },
    error: {  // red
      main: "#E03C6C",
    },
    background: {  // black
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
    md: {
      height: 110,
      marginBottom: 86,
    }
  },
  footer: {
    height: 70,
  }
});
