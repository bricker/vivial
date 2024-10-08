import React from "react";
import { CookiesProvider, withCookies } from "react-cookie";
import { Helmet } from "react-helmet";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { CssBaseline, ThemeProvider } from "@mui/material";
import "../static/css/app.css";
import AuthenticationPage from "./components/Pages/AuthenticationPage";
import OutingPage from "./components/Pages/OutingPage";
import SurveyPage from "./components/Pages/SurveyPage";
import AppContextProvider from "./context/Provider";
import { theme } from "./theme";

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
              <Route path="/" element={<SurveyPage />} />
              <Route path="/signup" element={<AuthenticationPage type="signup" />} />
              <Route path="/login" element={<AuthenticationPage type="login" />} />
              <Route path="/outing/:outingId" element={<OutingPage />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </BrowserRouter>
        </ThemeProvider>
      </AppContextProvider>
    </CookiesProvider>
  );
};

export default withCookies(App);
