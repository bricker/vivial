import React, { useState, useEffect } from "react";
import axios from "axios";
import styles from "./styles.module.css";

function parseCookies() {
  const newCookieString = document.cookie.replaceAll(/; ?/g, "&");
  return new URLSearchParams(newCookieString);
}

const TodoList = () => {
  const cookies = parseCookies();
  const userId = cookies.get("user_id");
  if (!userId) {
    window.location.assign("/login");
    return;
  }

  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [inputValue, setInputValue] = useState("");

  const fetchTodos = () => {
    setLoading(true);
    axios.get("/api/todos")
      .then(response => {
        setTodos(response.data);
      })
      .catch(error => {
        console.error("Error fetching todos:", error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const addTodo = () => {
    if (inputValue.trim() !== "") {
      axios.post("/api/todos", { text: inputValue })
        .then(response => {
          setTodos([...todos, response.data]);
          setInputValue("");
        })
        .catch(error => {
          console.error("Error adding todo:", error);
        });
    }
  };

  const removeTodo = (id) => {
    axios.delete(`/api/todos/${id}`)
      .then(() => {
        setTodos(todos.filter(todo => todo.id !== id));
      })
      .catch(error => {
        console.error("Error deleting todo:", error);
      });
  };

  useEffect(() => {
    fetchTodos();
  }, []);

  return (
    <div>
      <h2 className={styles.header}>TODO List</h2>

      {(() => {
        if (loading) {
          return (
            <div className={styles.loadingContainer}>
              <div className={styles.loader}></div>
            </div>
          );
        } else {
          return (<>
            <div style={{display: "flex"}}>
              <input
                className={styles.input}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Enter a new todo..."
              />
              <button className={styles.button} onClick={addTodo}>Add</button>
            </div>
            <ul className={styles.list}>
              {todos.map(todo => (
                <li key={todo.id} className={styles.item}>
                  {todo.text}
                  <button className={styles.redbutton} onClick={() => removeTodo(todo.id)}>Remove</button>
                </li>
              ))}
            </ul>
          </>);
        }
      })()}
    </div>
  );
};

export default TodoList;
