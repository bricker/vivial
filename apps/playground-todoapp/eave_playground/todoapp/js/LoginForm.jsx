import React, { useState } from "react";
import axios from "axios";
import styles from "./styles.module.css";

const LoginForm = () => {
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      await axios.post("/api/login", { username });
      window.location.assign("/");
    } catch (error) {
      console.error("Login failed:", error);
      setError("Invalid login");
    }
  };

  return (
    <div>
      <h2>Login</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleLogin}>
        <div>
          <label className={styles.label} htmlFor="username">Username:</label>
          <input
            className={styles.input}
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <button className={styles.button} type="submit">Login</button>
      </form>
    </div>
  );
};

export default LoginForm;
