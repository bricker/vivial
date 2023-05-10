import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
} from 'react-router-dom';
import { CookiesProvider, withCookies } from 'react-cookie';
import { ThemeProvider } from '@material-ui/core';
import { Helmet } from 'react-helmet';

import AppStoreProvider from './context/Provider.js';
import theme from './theme/index.js';
import EarlyAccessPage from './components/Pages/EarlyAccessPage/index.jsx';
import HomePage from './components/Pages/HomePage/index.jsx';
import TermsPage from './components/Pages/TermsPage/index.jsx';
import PrivacyPage from './components/Pages/PrivacyPage/index.jsx';
import ScrollToTop from './components/ScrollToTop/index.jsx';
import ThanksPage from './components/Pages/ThanksPage/index.jsx';
import PrivateRoutes from './components/PrivateRoutes/index.jsx';
import Dashboard from './components/Pages/Dashboard/index.jsx';

class App extends React.Component {
  render() {
    return (
      <CookiesProvider>
        <AppStoreProvider>
          <ThemeProvider theme={theme}>
            <Helmet>
                <title>Eave, for your information.</title>
            </Helmet>
            <Router>
              <ScrollToTop />
              <Routes>
                <Route path="/early" element={<EarlyAccessPage pageTitle="Early access submission" />} />
                <Route path="/terms" element={<TermsPage />} />
                <Route path="/privacy" element={<PrivacyPage />} />
                <Route element={<PrivateRoutes />}>
                  <Route path="/thanks" element={<ThanksPage />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                </Route>
                <Route path="/" element={<HomePage />} />
              </Routes>
            </Router>
          </ThemeProvider>
        </AppStoreProvider>
      </CookiesProvider>
    );
  }
}

export default withCookies(App);
