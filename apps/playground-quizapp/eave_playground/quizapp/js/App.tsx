import React from "react";
import ReactDOM from "react-dom/client";
import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";

import CookieConsentBanner from "./CookieBanner";
import QuizPage from "./Quiz";

const App = () => {
  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<QuizPage />} />
          <Route
            path="*"
            element={
              <Navigate
                to={{
                  pathname: "/",
                  search: window.location.search,
                }}
                replace
              />
            }
          />
        </Routes>
      </Router>
      <CookieConsentBanner />
    </>
  );
};

const root = ReactDOM.createRoot(document.getElementById("root")!);
root.render(<App />);
