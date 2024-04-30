import logo from './logo.svg';
import {  Link } from 'react-router-dom';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        
        <a href="https://google.com">External link</a>
        
        <Link
          className="App-link"
          to="/page"
        >
          Go to subpage
        </Link>
      </header>
    </div>
  );
}

export default App;
