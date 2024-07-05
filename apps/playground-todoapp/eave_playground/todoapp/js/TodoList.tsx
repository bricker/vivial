import axios from "axios";
import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import styles from "./TodoList.module.css";
import { COOKIE_PREFIX, getCookie } from "./cookies";
import { TodoListItem, TodoSummary } from "./types";

const TodoList = () => {
  const userId = getCookie(`${COOKIE_PREFIX}user_id`);
  const navigate = useNavigate();

  useEffect(() => {
    if (!userId) {
      navigate({ pathname: "/login", search: window.location.search }, { replace: true });
    }
  }, [userId]);

  if (!userId) {
    return null;
  }

  const username = getCookie(`${COOKIE_PREFIX}user_name`);

  const [todos, setTodos] = useState<TodoListItem[]>([]);
  const [summary, setSummary] = useState<TodoSummary | null>(null);
  const [summaryLoading, setSummaryLoading] = useState<boolean>(false);
  const [loading, setLoading] = useState(true);
  const [inputValue, setInputValue] = useState("");
  const [editingTodoId, setEditingTodo] = useState<TodoListItem | null>(null);
  const [editText, setEditText] = useState<string>("");

  const fetchTodos = () => {
    setLoading(true);
    axios
      .get<TodoListItem[]>("/api/todos")
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

  const summarize = () => {
    setSummaryLoading(true);
    axios
      .get<TodoSummary>("/api/summary")
      .then((response) => {
        setSummary(response.data);
        setSummaryLoading(false);
      })
      .catch((error) => {
        console.error(error);
        setSummaryLoading(false);
      });
  };

  const addTodo = () => {
    if (inputValue.trim() !== "") {
      axios
        .post<TodoListItem>("/api/todos", { text: inputValue })
        .then((response) => {
          setTodos([...todos, response.data]);
          setInputValue("");
        })
        .catch((error) => {
          console.error("Error adding todo:", error);
        });
    }
  };

  const removeTodo = (todo: TodoListItem) => {
    axios
      .delete(`/api/todos/${todo.id}`)
      .then(() => {
        setTodos(todos.filter((t) => t.id !== todo.id));
      })
      .catch((error) => {
        console.error("Error deleting todo:", error);
      });
  };

  const updateTodo = (todo: TodoListItem) => {
    axios
      .patch(`/api/todos/${todo.id}`, { text: editText })
      .then(() => {
        setTodos(
          todos.map((t) => {
            if (t.id === todo.id) {
              return { ...t, text: editText };
            }
            return t;
          }),
        );
        setEditingTodo(null);
        setEditText("");
      })
      .catch((error) => {
        console.error("Error updating todo:", error);
      });
  };

  const handleEdit = (todo: TodoListItem, text: string) => {
    setEditingTodo(todo);
    setEditText(text);
  };

  const cancelEdit = () => {
    setEditingTodo(null);
    setEditText("");
  };

  useEffect(() => {
    fetchTodos();
  }, []);

  return (
    <div className={styles.todoList}>
      <h2 className={styles.title}>TODO List</h2>
      <p>
        Logged in as <strong>{username}</strong> (
        <Link to="/logout" reloadDocument>
          Change
        </Link>
        )
      </p>

      {loading ? (
        <div className={styles.loadingContainer}>
          <div className={styles.loader}></div>
        </div>
      ) : (
        <>
          <div className={styles.summaryContainer}>
            <button onClick={summarize} className={styles.addButton}>
              Summarize
            </button>

            {summaryLoading ? (
              <div className={styles.loadingContainer}>
                <div className={styles.loader}></div>
              </div>
            ) : summary ? (
              <p className={styles.todoSummary}>{summary.text}</p>
            ) : null}
          </div>

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
                {editingTodoId && editingTodoId.id === todo.id ? (
                  <>
                    <input
                      type="text"
                      autoFocus
                      value={editText}
                      onChange={(e) => setEditText(e.target.value)}
                      className={styles.editInput}
                    />
                    <button onClick={() => updateTodo(todo)} className={styles.saveButton}>
                      Save
                    </button>
                    <button onClick={cancelEdit} className={styles.cancelButton}>
                      Cancel
                    </button>
                  </>
                ) : (
                  <>
                    <span
                      onClick={() => {
                        handleEdit(todo, todo.text);
                      }}
                      className={styles.todoText}
                    >
                      {todo.text}
                    </span>
                    <button onClick={() => removeTodo(todo)} className={styles.removeButton}>
                      Remove
                    </button>
                  </>
                )}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
};

export default TodoList;
