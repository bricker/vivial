import { configureStore, createListenerMiddleware } from "@reduxjs/toolkit";
import { authSlice } from "./slices/authSlice";
import { coreApiSlice } from "./slices/coreApiSlice";

const listenerMiddleware = createListenerMiddleware();
const store = configureStore({
  reducer: {
    coreApi: coreApiSlice.reducer,
    auth: authSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().prepend(listenerMiddleware.middleware).concat(coreApiSlice.middleware),
});

export default store;
