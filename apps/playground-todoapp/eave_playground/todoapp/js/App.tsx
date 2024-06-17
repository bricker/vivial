import React from "react";
import ReactDOM from "react-dom/client";
import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";

import "../static/css/app.css";
import CookieConsentBanner from "./CookieBanner";
import LoginForm from "./LoginForm";
import TodoList from "./TodoList";

const App = () => {
  return (
    <>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginForm />} />
          <Route path="/" element={<TodoList />} />
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
