import { Link } from "react-router-dom";
import "./App.css";
import logo from "./logo.svg";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>

        <a href="https://google.com">External link</a>

        <Link className="App-link" to="/page">
          Go to subpage
        </Link>
        <Link className="App-link" to="/form">
          Go to form
        </Link>
      </header>
    </div>
  );
}

export default App;
