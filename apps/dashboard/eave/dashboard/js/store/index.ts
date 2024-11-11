import { configureStore } from "@reduxjs/toolkit";

import todosReducer from "./sample/sampleSlice";

// TODO: Delete todos sample.
const store = configureStore({
  reducer: {
    sample: todosReducer,
  },
});

export default store;
