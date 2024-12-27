import { CssBaseline, ThemeProvider } from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import React from "react";
import { CookiesProvider, withCookies } from "react-cookie";
import { Helmet } from "react-helmet";
import { Provider as StoreProvider } from "react-redux";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import BookingEditPage from "./components/Pages/BookingEditPage";
import RootPage from "./components/Pages/RootPage";
import { AppRoute } from "./routes";
import store from "./store";
import { theme } from "./theme";

const App = () => {
  return (
    <>
      <CssBaseline />
      <Helmet>
        <title>Vivial admin dash</title>
      </Helmet>
      <BrowserRouter>
        <Routes>
          <Route index element={<RootPage />} />
          <Route path={`${AppRoute.bookingEdit}/:bookingId`} element={<BookingEditPage />} />

          <Route path="*" element={<Navigate to={AppRoute.root} />} />
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
