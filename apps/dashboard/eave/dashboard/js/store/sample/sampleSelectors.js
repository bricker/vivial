// @ts-nocheck

import { createSelector } from "@reduxjs/toolkit";
import { todosAdapter } from "./sampleAdapter";

export const { selectAll: selectTodos, selectById: selectTodoById } = todosAdapter.getSelectors((state) => state.todos);

export const selectTodoIds = createSelector(
  // First, pass one or more "input selector" functions:
  selectTodos,
  // Then, an "output selector" that receives all the input results as arguments
  // and returns a final result value
  (todos) => todos.map((todo) => todo.id),
);

export const selectFilteredTodos = createSelector(
  // First input selector: all todos
  selectTodos,
  // Second input selector: all filter values
  (state) => state.filters,
  // Output selector: receives both values
  (todos, filters) => {
    const { status, colors } = filters;
    const showAllCompletions = status === "ALL";
    if (showAllCompletions && colors.length === 0) {
      return todos;
    }

    const completedStatus = status === "COMPLETED";
    // Return either active or completed todos based on filter
    return todos.filter((todo) => {
      const statusMatches = showAllCompletions || todo.completed === completedStatus;
      const colorMatches = colors.length === 0 || colors.includes(todo.color);
      return statusMatches && colorMatches;
    });
  },
);

export const selectFilteredTodoIds = createSelector(
  // Pass our other memoized selector as an input
  selectFilteredTodos,
  // And derive data in the output selector
  (filteredTodos) => filteredTodos.map((todo) => todo.id),
);
