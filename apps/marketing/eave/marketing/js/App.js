import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
} from 'react-router-dom';
import { CookiesProvider, withCookies } from 'react-cookie';
import { ThemeProvider } from '@material-ui/core';
import theme from './theme/index.js';
import AppStoreProvider from './context/Provider.js';
// views
import EarlyAccessPage from './components/Pages/EarlyAccessPage/index.js';
import HomePage from './components/Pages/HomePage/index.js';
import TermsPage from './components/Pages/TermsPage/index.jsx';
import PrivacyPage from './components/Pages/PrivacyPage/index.jsx';
import ScrollToTop from './components/ScrollToTop/index.jsx';
import ThanksPage from './components/Pages/ThanksPage/index.js';

class App extends React.Component {
  render() {
    return (
      <CookiesProvider>
        <AppStoreProvider>
          <ThemeProvider theme={theme}>
            <Router>
              <ScrollToTop />
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/early" element={<EarlyAccessPage pageTitle="Early access submission" />} />
                <Route path="/terms" element={<TermsPage />} />
                <Route path="/privacy" element={<PrivacyPage />} />
                <Route path='/thanks' element={<ThanksPage />} />
              </Routes>
            </Router>
          </ThemeProvider>
        </AppStoreProvider>
      </CookiesProvider>
    );
  }
}

export default withCookies(App);
