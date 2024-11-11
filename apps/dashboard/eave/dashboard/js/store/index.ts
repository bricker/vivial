import { configureStore } from "@reduxjs/toolkit";

import sampleReducer from "./sample/sampleSlice";

// TODO: Delete sample reducer.
const store = configureStore({
  reducer: {
    sample: sampleReducer,
  },
});

export default store;
