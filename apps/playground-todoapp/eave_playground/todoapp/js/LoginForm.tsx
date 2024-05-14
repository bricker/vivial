import axios from "axios";
import React, { FormEvent, useState } from "react";
import styles from "./LoginForm.module.css";

const LoginForm = () => {
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await axios.post("/api/login", { username });
      window.location.assign("/");
    } catch (ex) {
      console.error("Login failed:", ex);
      setError("System error.");
    }
  };

  return (
    <div className={styles.loginContainer}>
      <h2 className={styles.title}>Login</h2>
      {error && <p className={styles.error}>{error}</p>}
      <form onSubmit={handleLogin} className={styles.form}>
        <div className={styles.formGroup}>
          <label className={styles.label} htmlFor="username">
            Username:
          </label>
          <input
            className={styles.input}
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <button className={styles.button} type="submit">
          Login
        </button>
      </form>
    </div>
  );
};

export default LoginForm;
