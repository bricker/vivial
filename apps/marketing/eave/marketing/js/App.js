import { CssBaseline, ThemeProvider } from "@material-ui/core";
import React, { useEffect } from "react";
import { CookiesProvider, withCookies } from "react-cookie";
import { Helmet } from "react-helmet";
import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";

import AuthUser from "./components/AuthUser/index.jsx";
import Dashboard from "./components/Pages/Dashboard/index.jsx";
import HomePage from "./components/Pages/HomePage/index.jsx";
import PrivacyPage from "./components/Pages/PrivacyPage/index.jsx";
import TermsPage from "./components/Pages/TermsPage/index.jsx";
import PrivateRoutes from "./components/PrivateRoutes/index.jsx";
import ScrollToTop from "./components/ScrollToTop/index.jsx";
import AppStoreProvider from "./context/Provider.js";
import { theme } from "./theme.js";
import '../static/css/app.css';

const App = () => {
  return (
    <CookiesProvider>
      <AppStoreProvider>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Helmet>
            <title>Eave - for your information.</title>
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
};

export default withCookies(App);
