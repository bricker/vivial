import { createAsyncThunk } from "@reduxjs/toolkit";

const client = {
  get: () => {},
  post: () => {},
};

export const fetchTodos = createAsyncThunk("todos/fetchTodos", async () => {
  const response = await client.get("/fakeApi/todos");
  return response.todos;
});

export const saveNewTodo = createAsyncThunk("todos/saveNewTodo", async (text) => {
  const initialTodo = { text };
  const response = await client.post("/fakeApi/todos", { todo: initialTodo });
  return response.todo;
});
