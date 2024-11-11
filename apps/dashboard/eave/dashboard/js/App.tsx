import { CssBaseline, ThemeProvider } from "@mui/material";
import React from "react";
import { CookiesProvider, withCookies } from "react-cookie";
import { Helmet } from "react-helmet";
import { Provider as StoreProvider } from "react-redux";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { pageView } from "./analytics/segment";
import DateSurveyPage from "./components/Pages/DateSurveyPage";
import RouteChangeTracker from "./components/RouteChangeTracker";
import store from "./store";
import { theme } from "./theme";

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
            <title>Vivial</title>
          </Helmet>
          <BrowserRouter>
            <RouteChangeTracker onRouteChange={fireAnalyticsPageView} />
            <Routes>
              <Route path="/" element={<DateSurveyPage />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </BrowserRouter>
        </ThemeProvider>
      </CookiesProvider>
    </StoreProvider>
  );
};

export default withCookies(App);
