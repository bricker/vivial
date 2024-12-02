import { CssBaseline, ThemeProvider } from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import React from "react";
import { CookiesProvider, withCookies } from "react-cookie";
import { Helmet } from "react-helmet";
import { Provider as StoreProvider, useSelector } from "react-redux";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { pageView } from "./analytics/segment";
import store, { RootState } from "./store";
import { theme } from "./theme";

import GlobalLayout from "./components/Global/GlobalLayout";
import AccountPage from "./components/Pages/AccountPage";
import AccountPreferencesPage from "./components/Pages/AccountPreferencesPage";
import BookingConfirmationPage from "./components/Pages/BookingConfirmationPage/index";
import DateSurveyPage from "./components/Pages/DateSurveyPage";
import ForgotPasswordPage from "./components/Pages/ForgotPasswordPage";
import HelpPage from "./components/Pages/HelpPage";
import LogInPage from "./components/Pages/LogInPage";
import PasswordResetPage from "./components/Pages/PasswordResetPage";
import PaymentExamplePage from "./components/Pages/PaymentExamplePage/index";
import PlansPage from "./components/Pages/PlansPage";
import PrivacyPage from "./components/Pages/PrivacyPage";
import SignUpPage from "./components/Pages/SignUpPage";
import TermsPage from "./components/Pages/TermsPage";
import StripeElementsProvider from "./components/StripeElementsProvider";
import { PrivateRoutes } from "./components/Util/PrivateRoutes";
import RouteChangeTracker from "./components/Util/RouteChangeTracker";
import ScrollToTop from "./components/Util/ScrollToTop";
import { AppContextProvider } from "./context";
import { AppRoute } from "./routes";

const fireAnalyticsPageView = (path: string) => pageView({ name: path });

const App = () => {
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);
  return (
    <>
      <CssBaseline />
      <Helmet>
        <title>Vivial - One Click Date Picked</title>
      </Helmet>
      <BrowserRouter>
        <ScrollToTop />
        <RouteChangeTracker onRouteChange={fireAnalyticsPageView} />
        <Routes>
          <Route path={AppRoute.root} element={<GlobalLayout />}>
            {/* always public routes */}
            <Route index element={<DateSurveyPage />} />
            <Route path={AppRoute.terms} element={<TermsPage />} />
            <Route path={AppRoute.privacy} element={<PrivacyPage />} />

            {/* un-authed only routes */}
            <Route element={<PrivateRoutes hasPermissions={!isLoggedIn} redirectPath={AppRoute.root} />}>
              <Route path={AppRoute.login} element={<LogInPage />} />
              <Route path={AppRoute.signup} element={<SignUpPage />} />
              <Route path={AppRoute.forgotPassword} element={<ForgotPasswordPage />} />
            </Route>

            {/* auth only routes */}
            <Route element={<PrivateRoutes hasPermissions={!!isLoggedIn} redirectPath={AppRoute.login} />}>
              <Route path={AppRoute.account} element={<AccountPage />} />
              <Route path={AppRoute.plans} element={<PlansPage />} />
              <Route path={AppRoute.help} element={<HelpPage />} />
              <Route path={AppRoute.bookingConfirmation} element={<BookingConfirmationPage />} />
              <Route path={AppRoute.passwordReset} element={<PasswordResetPage />} />
              <Route path={AppRoute.accountPreferences} element={<AccountPreferencesPage />} />
            </Route>

            {/* TODO: Remove /payment-example Route. */}
            <Route
              path={AppRoute.payment}
              element={
                <StripeElementsProvider>
                  <PaymentExamplePage />
                </StripeElementsProvider>
              }
            />

            <Route path="*" element={<Navigate to={AppRoute.root} />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </>
  );
};

const ProviderWrappedApp = () => {
  return (
    <StoreProvider store={store}>
      {/* TODO: Remove AppContextProvider in favor of Redux. */}
      <AppContextProvider>
        <CookiesProvider>
          <ThemeProvider theme={theme}>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <App />
            </LocalizationProvider>
          </ThemeProvider>
        </CookiesProvider>
      </AppContextProvider>
    </StoreProvider>
  );
};

export default withCookies(ProviderWrappedApp);
