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
import BookingConfirmationPage from "./components/Pages/BookingConfirmationPage/index";
import DateSurveyPage from "./components/Pages/DateSurveyPage";
import ForgotPasswordPage from "./components/Pages/ForgotPasswordPage";
import LogInPage from "./components/Pages/LogInPage";
import PaymentExamplePage from "./components/Pages/PaymentExamplePage/index";
import PrivacyPage from "./components/Pages/PrivacyPage";
import SignUpPage from "./components/Pages/SignUpPage";
import TermsPage from "./components/Pages/TermsPage";
import StripeElementsProvider from "./components/StripeElementsProvider";
import RouteChangeTracker from "./components/Util/RouteChangeTracker";
import ScrollToTop from "./components/Util/ScrollToTop";
import { AppContextProvider } from "./context";

const App = () => {
  const fireAnalyticsPageView = async (_: string) => {
    await pageView({});
  };

  return (
    <StoreProvider store={store}>
      <AppContextProvider>
        <CookiesProvider>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <Helmet>
              <title>Vivial - One Click Date Picked</title>
            </Helmet>
            <BrowserRouter>
              <ScrollToTop />
              <RouteChangeTracker onRouteChange={fireAnalyticsPageView} />
              <Routes>
                <Route path="/" element={<GlobalLayout />}>
                  <Route index element={<DateSurveyPage />} />
                  <Route path="/login" element={<LogInPage />} />
                  <Route path="/login/password" element={<ForgotPasswordPage />} />
                  <Route path="/signup" element={<SignUpPage />} />
                  <Route path="/terms" element={<TermsPage />} />
                  <Route path="/privacy" element={<PrivacyPage />} />
                  <Route path="/booking-confirmation" element={<BookingConfirmationPage />} />

                  <Route
                    path="/payment-example"
                    element={
                      <StripeElementsProvider>
                        <PaymentExamplePage />
                      </StripeElementsProvider>
                    }
                  />

                  <Route path="*" element={<Navigate to="/" />} />
                </Route>
              </Routes>
            </BrowserRouter>
          </ThemeProvider>
        </CookiesProvider>
      </AppContextProvider>
    </StoreProvider>
  );
};

export default withCookies(App);
