import { CssBaseline, ThemeProvider } from "@mui/material";
import React from "react";
import { CookiesProvider, withCookies } from "react-cookie";
import { Helmet } from "react-helmet";
import { Provider } from "react-redux";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import "../static/css/app.css";
import AuthenticationPage from "./components/Pages/AuthenticationPage";
import { Dashboard } from "./components/Pages/Dashboard";
import Glossary from "./components/Pages/Dashboard/Glossary/index";
import Insights from "./components/Pages/Dashboard/Insights/index";
import Settings from "./components/Pages/Dashboard/Settings/index";
import Setup from "./components/Pages/Dashboard/Setup/index";
import TeamManagement from "./components/Pages/Dashboard/TeamManagement/index";
import Onboarding from "./components/Pages/Onboarding";
import Waitlist from "./components/Pages/Waitlist";
import AppContextProvider from "./context/Provider";
import store from "./store";
import { theme } from "./theme";

const App = () => {
  return (
    <CookiesProvider>
      <AppContextProvider>
        <Provider store={store}>
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
                  <Route path="/setup" element={<Setup />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/glossary" element={<Glossary />} />
                  <Route path="/insights" element={<Insights />} />
                  <Route path="/team" element={<TeamManagement />} />
                </Route>

                <Route path="/onboarding" element={<Onboarding />} />
                <Route path="/waitlist" element={<Waitlist />} />

                <Route path="*" element={<Navigate to="/onboarding" />} />
              </Routes>
            </BrowserRouter>
          </ThemeProvider>
        </Provider>
      </AppContextProvider>
    </CookiesProvider>
  );
};

export default withCookies(App);
