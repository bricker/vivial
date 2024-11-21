// @ts-nocheck

import { createSlice } from "@reduxjs/toolkit";
import { fetchTodos, saveNewTodo } from "./sampleThunks.js";

import { todosAdapter } from "./sampleAdapter.js";

const todosSlice = createSlice({
  name: "todos",
  initialState: todosAdapter.getInitialState({
    status: "idle",
  }),
  reducers: {
    todoToggled(state, action) {
      const todoId = action.payload;
      const todo = state.entities[todoId];
      todo.completed = !todo.completed;
    },
    todoColorSelected: {
      reducer(state, action) {
        const { color, todoId } = action.payload;
        state.entities[todoId].color = color;
      },
      prepare(todoId, color) {
        return {
          payload: { todoId, color },
        };
      },
    },
    todoDeleted: todosAdapter.removeOne,
    // eslint-disable-next-line no-unused-vars
    allTodosCompleted(state, action) {
      Object.values(state.entities).forEach((todo) => {
        todo.completed = true;
      });
    },
    // eslint-disable-next-line no-unused-vars
    completedTodosCleared(state, action) {
      const completedIds = Object.values(state.entities)
        .filter((todo) => todo.completed)
        .map((todo) => todo.id);
      todosAdapter.removeMany(state, completedIds);
    },
  },
  extraReducers: (builder) => {
    builder
      // eslint-disable-next-line no-unused-vars
      .addCase(fetchTodos.pending, (state, action) => {
        state.status = "loading";
      })
      .addCase(fetchTodos.fulfilled, (state, action) => {
        todosAdapter.setAll(state, action.payload);
        state.status = "idle";
      })
      .addCase(saveNewTodo.fulfilled, todosAdapter.addOne);
  },
});

export const { allTodosCompleted, completedTodosCleared, todoAdded, todoColorSelected, todoDeleted, todoToggled } =
  todosSlice.actions;

export default todosSlice.reducer;
