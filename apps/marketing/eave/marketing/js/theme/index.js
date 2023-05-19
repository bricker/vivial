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
      secondary: '#BFDDFF',
    },
  },
  typography: {
    color: {
      light: '#FFFFFF',
      main: '#3E3E3E',
      dark: '#000000',
      innactive: '#808182',
      link: '#1A2697',
    },
    fontFamily: ['DM Sans', 'sans-serif'],
  },
});

export default theme;
