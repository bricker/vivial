import { configureStore, createListenerMiddleware } from "@reduxjs/toolkit";
import { authSlice } from "./slices/authSlice";
import { coreApiSlice } from "./slices/coreApiSlice";
import { reserverDetailsSlice } from "./slices/reserverDetailsSlice";

const listenerMiddleware = createListenerMiddleware();
const store = configureStore({
  reducer: {
    coreApi: coreApiSlice.reducer,
    auth: authSlice.reducer,
    reserverDetails: reserverDetailsSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().prepend(listenerMiddleware.middleware).concat(coreApiSlice.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export default store;
