import { CssBaseline, ThemeProvider } from "@mui/material";
import React from "react";
import { CookiesProvider, withCookies } from "react-cookie";
import { Helmet } from "react-helmet";
import { Provider as StoreProvider } from "react-redux";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { pageView } from "./analytics/segment";
import store from "./store";
import { theme } from "./theme";

import GlobalLayout from "./components/Global/GlobalLayout";
import DateSurveyPage from "./components/Pages/DateSurveyPage";
import LogInPage from "./components/Pages/LogInPage";
import PrivacyPage from "./components/Pages/PrivacyPage";
import TermsPage from "./components/Pages/TermsPage";
import RouteChangeTracker from "./components/Util/RouteChangeTracker";

const App = () => {
  const fireAnalyticsPageView = async (_: string) => {
    await pageView({});
  };

  return (
    <StoreProvider store={store}>
      <CookiesProvider>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Helmet>
            <title>Vivial - One Click Date Picked</title>
          </Helmet>
          <BrowserRouter>
            <RouteChangeTracker onRouteChange={fireAnalyticsPageView} />
            <Routes>
              <Route path="/" element={<GlobalLayout />}>
                <Route index element={<DateSurveyPage />} />
                <Route path="/login" element={<LogInPage />} />
                <Route path="/terms" element={<TermsPage />} />
                <Route path="/privacy" element={<PrivacyPage />} />
                <Route path="*" element={<Navigate to="/" />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </ThemeProvider>
      </CookiesProvider>
    </StoreProvider>
  );
};

export default withCookies(App);
