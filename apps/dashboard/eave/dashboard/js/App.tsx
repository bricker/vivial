import React from "react";
import { CookiesProvider, withCookies } from "react-cookie";
import { Helmet } from "react-helmet";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { CssBaseline, ThemeProvider } from "@mui/material";
import "../static/css/app.css";
import AuthenticationPage from "./components/Pages/AuthenticationPage";
import AppContextProvider from "./context/Provider";
import { theme } from "./theme";
import DateGenerator from "./components/Pages/DateGenerator";

const App = () => {
  return (
    <CookiesProvider>
      <AppContextProvider>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Helmet>
            <title>Vivial</title>
          </Helmet>
          <BrowserRouter>
            <Routes>
              <Route path="" element={<DateGenerator />} />
              <Route path="/signup" element={<AuthenticationPage type="signup" />} />
              <Route path="/login" element={<AuthenticationPage type="login" />} />

              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </BrowserRouter>
        </ThemeProvider>
      </AppContextProvider>
    </CookiesProvider>
  );
};

export default withCookies(App);
