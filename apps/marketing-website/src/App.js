import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
} from 'react-router-dom';
import { CookiesProvider, withCookies } from 'react-cookie';
import { ThemeProvider } from '@material-ui/core';
import theme from './theme';
import EarlyAccessPage from './components/Pages/EarlyAccessPage';
import HomePage from './components/Pages/HomePage';

class App extends React.Component {
  render() {
    return (
      <CookiesProvider>
        <ThemeProvider theme={theme}>
          <Router>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/early" element={<EarlyAccessPage pageTitle="Early access submission" />} />
            </Routes>
          </Router>
        </ThemeProvider>
      </CookiesProvider>
    );
  }
}

export default withCookies(App);
