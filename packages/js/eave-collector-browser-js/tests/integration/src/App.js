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
            <Link id="logout" to="/logout">
              Log out
            </Link>
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
