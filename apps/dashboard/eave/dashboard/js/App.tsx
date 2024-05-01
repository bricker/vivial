import React from "react";
import { CookiesProvider, withCookies } from "react-cookie";
import { Helmet } from "react-helmet";
import {
  Navigate,
  Route,
  BrowserRouter as Router,
  Routes,
} from "react-router-dom";

import { CssBaseline, ThemeProvider } from "@mui/material";
import "../static/css/app.css";
import AuthenticationPage from "./components/Pages/AuthenticationPage";
import Dashboard from "./components/Pages/Dashboard";
import ScrollToTop from "./components/ScrollToTop";
import AppContextProvider from "./context/Provider";
import { theme } from "./theme";

const App = () => {
  return (
    <CookiesProvider>
      <AppContextProvider>
        <ThemeProvider theme={theme}>
          <CssBaseline />
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
              <Route path="/insights" element={<Dashboard page="insights" />} />
              <Route path="/glossary" element={<Dashboard page="glossary" />} />
              <Route path="/settings" element={<Dashboard page="settings" />} />
              <Route path="/team" element={<Dashboard page="team" />} />

              <Route path="*" element={<Navigate to="/insights" />} />
            </Routes>
          </Router>
        </ThemeProvider>
      </AppContextProvider>
    </CookiesProvider>
  );
};

export default withCookies(App);
