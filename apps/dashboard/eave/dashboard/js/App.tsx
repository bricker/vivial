import { CssBaseline, ThemeProvider } from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import mixpanel from "mixpanel-browser";
import React from "react";
import { CookiesProvider, withCookies } from "react-cookie";
import { Helmet } from "react-helmet";
import { Provider as StoreProvider, useSelector } from "react-redux";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { initMixpanelSessionRecording } from "./analytics/mixpanel";
import { pageView } from "./analytics/segment";
import GlobalLayout from "./components/Global/GlobalLayout";
import AccountPage from "./components/Pages/AccountPage";
import AccountPreferencesPage from "./components/Pages/AccountPreferencesPage";
import BookingDetailsPage from "./components/Pages/BookingDetailsPage";
import CheckoutCompletePage from "./components/Pages/CheckoutCompletePage";
import CheckoutReservationPage from "./components/Pages/CheckoutReservationPage";
import DateItineraryPage from "./components/Pages/DateItineraryPage";
import DateSurveyPage from "./components/Pages/DateSurveyPage";
import ForgotPasswordPage from "./components/Pages/ForgotPasswordPage";
import HelpPage from "./components/Pages/HelpPage";
import LogInPage from "./components/Pages/LogInPage";
import PasswordResetPage from "./components/Pages/PasswordResetPage";
import PlansPage from "./components/Pages/PlansPage";
import PrivacyPage from "./components/Pages/PrivacyPage";
import SignUpPage from "./components/Pages/SignUpPage";
import StripeCustomerPortal from "./components/Pages/StripeCustomerPortal";
import TermsPage from "./components/Pages/TermsPage";
import { PrivateRoutes } from "./components/Util/PrivateRoutes";
import RouteChangeTracker from "./components/Util/RouteChangeTracker";
import ScrollToTop from "./components/Util/ScrollToTop";
import { AppRoute } from "./routes";
import store, { RootState } from "./store";
import { theme } from "./theme";

const fireAnalyticsPageView = (_path: string) => pageView({});

initMixpanelSessionRecording();

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
            <Route path={AppRoute.itinerary} element={<DateItineraryPage />} />
            <Route path={AppRoute.terms} element={<TermsPage />} />
            <Route path={AppRoute.privacy} element={<PrivacyPage />} />

            {/* un-authed only routes */}
            <Route element={<PrivateRoutes hasPermissions={!isLoggedIn} redirectPath={AppRoute.root} />}>
              <Route path={AppRoute.login} element={<LogInPage />} />
              <Route path={AppRoute.signup} element={<SignUpPage />} />
              <Route path={AppRoute.forgotPassword} element={<ForgotPasswordPage />} />
            </Route>

            {/* auth only routes - login redirect */}
            <Route element={<PrivateRoutes hasPermissions={!!isLoggedIn} redirectPath={AppRoute.login} />}>
              <Route path={AppRoute.account} element={<AccountPage />} />
              <Route path={AppRoute.plans} element={<PlansPage />} />
              <Route path={AppRoute.planDetails} element={<BookingDetailsPage />} />
              <Route path={AppRoute.help} element={<HelpPage />} />
              <Route path={AppRoute.passwordReset} element={<PasswordResetPage />} />
              <Route path={AppRoute.billing} element={<StripeCustomerPortal />} />
              <Route path={AppRoute.accountPreferences} element={<AccountPreferencesPage />} />
              <Route path={AppRoute.checkoutComplete} element={<CheckoutCompletePage />} />
            </Route>

            {/* auth only routes - signup redirect */}
            <Route element={<PrivateRoutes hasPermissions={!!isLoggedIn} redirectPath={AppRoute.signup} />}>
              <Route path={AppRoute.checkoutReserve} element={<CheckoutReservationPage />} />
            </Route>

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
      <CookiesProvider>
        <ThemeProvider theme={theme}>
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <App />
          </LocalizationProvider>
        </ThemeProvider>
      </CookiesProvider>
    </StoreProvider>
  );
};

export default withCookies(ProviderWrappedApp);
