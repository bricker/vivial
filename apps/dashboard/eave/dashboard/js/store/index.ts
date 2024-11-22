import { configureStore, createListenerMiddleware } from "@reduxjs/toolkit";
import { coreApiSlice } from "./slices/coreApiSlice";
import { authSlice } from "./slices/authSlice"

const listenerMiddleware = createListenerMiddleware()
const store = configureStore({
  reducer: {
    coreApi: coreApiSlice.reducer,
    auth: authSlice.reducer,
  },
  middleware: getDefaultMiddleware =>
    getDefaultMiddleware()
      .prepend(listenerMiddleware.middleware)
      .concat(coreApiSlice.middleware)
});

export default store;
