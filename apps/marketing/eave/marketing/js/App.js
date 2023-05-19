import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import { CookiesProvider, withCookies } from 'react-cookie';
import { ThemeProvider, CssBaseline } from '@material-ui/core';
import { Helmet } from 'react-helmet';

import AppStoreProvider from './context/Provider.js';
import theme from './theme/index.js';
import HomePage from './components/Pages/HomePage/index.jsx';
import TermsPage from './components/Pages/TermsPage/index.jsx';
import PrivacyPage from './components/Pages/PrivacyPage/index.jsx';
import ScrollToTop from './components/ScrollToTop/index.jsx';
import PrivateRoutes from './components/PrivateRoutes/index.jsx';
import Dashboard from './components/Pages/Dashboard/index.jsx';
import AuthUser from './components/AuthUser/index.jsx';

class App extends React.Component {
  render() {
    return (
      <CookiesProvider>
        <AppStoreProvider>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <Helmet>
                <title>Eave, for your information.</title>
            </Helmet>
            <AuthUser>
              <Router>
                <ScrollToTop />
                <Routes>
                  <Route path="/terms" element={<TermsPage />} />
                  <Route path="/privacy" element={<PrivacyPage />} />
                  <Route element={<PrivateRoutes />}>
                    <Route path="/dashboard" element={<Dashboard />} />
                  </Route>
                  <Route path="/" element={<HomePage />} />
                  <Route path="*" element={<Navigate to="/" />} />
                </Routes>
              </Router>
            </AuthUser>
          </ThemeProvider>
        </AppStoreProvider>
      </CookiesProvider>
    );
  }
}

export default withCookies(App);
