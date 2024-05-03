import { useState } from "react";
import { Link } from "react-router-dom";
import "./App.css";
import logo from "./logo.svg";

function App() {
  const [counter, setCounter] = useState(0);

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <p>Counter {counter}</p>
        <button id="counter-btn" onClick={() => setCounter(counter + 1)}>counter++</button>

        <a href="https://google.com">External link</a>

        <Link id="page-link" className="App-link" to="/page">
          Go to subpage
        </Link>
        <Link id="form-link" className="App-link" to="/form">
          Go to form
        </Link>
      </header>
    </div>
  );
}

export default App;
