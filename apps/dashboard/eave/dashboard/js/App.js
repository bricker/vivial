// @ts-check
import { CssBaseline, ThemeProvider } from "@material-ui/core";
import React from "react";
import { CookiesProvider, withCookies } from "react-cookie";
import { Helmet } from "react-helmet";
import {
  Navigate,
  Route,
  BrowserRouter as Router,
  Routes,
} from "react-router-dom";

import "../static/css/app.css";
// import HomePage from "./components/Pages/HomePage/index.jsx";
import AuthenticationPage from "./components/Pages/AuthenticationPage/index.jsx";
import EventDashboard from "./components/Pages/EventDashboard/index.jsx";
import ScrollToTop from "./components/ScrollToTop/index.jsx";
import AppContextProvider from "./context/Provider.js";
import { theme } from "./theme.js";

const App = () => {
  return (
    <CookiesProvider>
      <AppContextProvider>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          {/* @ts-ignore */}
          <Helmet>
            <title>Eave - for your information.</title>
          </Helmet>
          <Router>
            <ScrollToTop />
            <Routes>
              <Route
                path="/signup"
                element={<AuthenticationPage type="signup" />}
              />

              <Route
                path="/login"
                element={<AuthenticationPage type="login" />}
              />
              <Route path="/" element={<EventDashboard />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </Router>
        </ThemeProvider>
      </AppContextProvider>
    </CookiesProvider>
  );
};

export default withCookies(App);
