import React from "react";
import { CookiesProvider, withCookies } from "react-cookie";
import { Helmet } from "react-helmet";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { CssBaseline, ThemeProvider } from "@mui/material";
import "../static/css/app.css";
import AuthenticationPage from "./components/Pages/AuthenticationPage";
import { Dashboard, TabRevealer } from "./components/Pages/Dashboard";
import Onboarding from "./components/Pages/Dashboard/Onboarding";
import Setup from "./components/Pages/Dashboard/Onboarding/setup";
import Waitlist from "./components/Pages/Dashboard/Onboarding/waitlist";
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
          <BrowserRouter>
            <Routes>
              <Route path="/signup" element={<AuthenticationPage type="signup" />} />

              <Route path="/login" element={<AuthenticationPage type="login" />} />

              <Route element={<Dashboard />}>
                <Route path="/insights" element={<TabRevealer name="insightsTab" pathname="/insights" />} />
                <Route path="/glossary" element={<TabRevealer name="glossaryTab" pathname="/glossary" />} />
                <Route path="/settings" element={<TabRevealer name="settingsTab" pathname="/settings" />} />
                <Route path="/team" element={<TabRevealer name="teamTab" pathname="/team" />} />
              </Route>

              <Route path="/onboarding" element={<Onboarding />} />
              <Route path="/waitlist" element={<Waitlist />} />
              <Route path="/setup" element={<Setup />} />

              <Route path="*" element={<Navigate to="/insights" />} />
            </Routes>
          </BrowserRouter>
        </ThemeProvider>
      </AppContextProvider>
    </CookiesProvider>
  );
};

export default withCookies(App);
