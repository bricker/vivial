import React, { useState } from "react";
import { useCookies } from "react-cookie";
import { Link } from "react-router-dom";
import "./App.css";
import logo from "./logo.svg";
import { AUTH_COOKIE_NAME } from "./util/cookies";

function App() {
  const [counter, setCounter] = useState(0);
  const [cookies, setCookie, removeCookie] = useCookies([AUTH_COOKIE_NAME]);
  const isLoggedIn = cookies[AUTH_COOKIE_NAME];

  return (
    <div className="App">
      <header className="App-header">
        <div className="auth-bar">
          {isLoggedIn && <p>You're logged in!</p>}
          {isLoggedIn ? (
            // stupid fancy logout button
            <div
              style={{
                backgroundColor: "#ff6b6b",
                border: "none",
                color: "white",
                textAlign: "center",
                textDecoration: "none",
                display: "inline-block",
                fontSize: "16px",
                margin: "4px 2px",
                cursor: "pointer",
                borderRadius: "12px",
              }}
            >
              <Link
                id="logout"
                style={{
                  display: "flex",
                  flexDirection: "row",
                  alignItems: "center",
                  padding: "10px 20px",
                }}
                to="/logout"
              >
                <svg
                  style={{ width: 24, height: 24 }}
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  ariaLabelledby="sign-out-svg"
                  aria-hidden="true"
                  role="img"
                >
                  <title id="sign-out-svg">Sign Out</title>
                  <path d="M15 15a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v5a1 1 0 1 1-2 0V4H6v16h8v-4a1 1 0 0 1 1-1zm8.923-2.618a1 1 0 0 1-.217.326l-4 3.999A.993.993 0 0 1 19 17a.999.999 0 0 1-.707-1.707L20.586 13H15a1 1 0 0 1 0-2h5.586l-2.293-2.293a.999.999 0 1 1 1.414-1.414l3.999 4a.992.992 0 0 1 .217 1.089z"></path>
                </svg>
                <div>
                  <h5>Log Out</h5>
                </div>
              </Link>
            </div>
          ) : (
            <button
              id="login"
              onClick={() => {
                setCookie(AUTH_COOKIE_NAME, "1");
              }}
            >
              Mock Login
            </button>
          )}
        </div>

        <img id="react-img" src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <p>Counter {counter}</p>
        <button id="counter-btn" onClick={() => setCounter(counter + 1)}>
          counter++
        </button>

        <a id="external-link" href="https://google.com">
          External link
        </a>

        <a id="page-internal-link" href="#">
          To top of page
        </a>

        <Link id="page-link" className="App-link" to="/page">
          Go to subpage
        </Link>
        <Link id="form-link" className="App-link" to="/form">
          Go to form
        </Link>

        <a href="#">
          <button id="btn-internal-link">Button in internal link</button>
        </a>

        <a href="https://google.com">
          <button id="btn-external-link">Button in external link</button>
        </a>
      </header>
    </div>
  );
}

export default App;
