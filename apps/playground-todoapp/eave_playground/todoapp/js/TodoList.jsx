import axios from "axios";
import React, { useEffect, useState } from "react";
import styles from "./TodoList.module.css";

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
    axios
      .get("/api/todos")
      .then((response) => {
        setTodos(response.data);
      })
      .catch((error) => {
        console.error("Error fetching todos:", error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const addTodo = () => {
    if (inputValue.trim() !== "") {
      axios
        .post("/api/todos", { text: inputValue })
        .then((response) => {
          setTodos([...todos, response.data]);
          setInputValue("");
        })
        .catch((error) => {
          console.error("Error adding todo:", error);
        });
    }
  };

  const removeTodo = (id) => {
    axios
      .delete(`/api/todos/${id}`)
      .then(() => {
        setTodos(todos.filter((todo) => todo.id !== id));
      })
      .catch((error) => {
        console.error("Error deleting todo:", error);
      });
  };

  useEffect(() => {
    fetchTodos();
  }, []);

  return (
    <div className={styles.todoList}>
      <h2 className={styles.title}>TODO List</h2>

      {loading ? (
        <div className={styles.loadingContainer}>
          <div className={styles.loader}></div>
        </div>
      ) : (
        <>
          <div className={styles.inputContainer}>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Enter a new todo..."
              className={styles.input}
            />
            <button onClick={addTodo} className={styles.addButton}>
              Add
            </button>
          </div>
          <ul className={styles.todoItems}>
            {todos.map((todo) => (
              <li key={todo.id} className={styles.todoItem}>
                {todo.text}
                <button
                  onClick={() => removeTodo(todo.id)}
                  className={styles.removeButton}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
};

export default TodoList;
