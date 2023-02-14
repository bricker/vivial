import { createTheme } from '@material-ui/core';

// Defaults: https://mui.com/material-ui/customization/theming/
const theme = createTheme({
  palette: {
    primary: {
      main: '#512DA8',
      dark: '#2C0E74',
    },
    background: {
      main: '#FDFDFD',
      dark: '#F1F1F1',
    },
  },
  typography: {
    color: {
      light: '#FFFFFF',
      main: '#3E3E3E',
      dark: '#000000',
    },
    fontFamily: {
      main: "'DM Sans', sans-serif",
      logo: "'Pattaya', sans-serif",
    },
  },
});

export default theme;
