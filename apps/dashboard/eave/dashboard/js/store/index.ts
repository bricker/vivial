import { StateFromReducersMapObject, configureStore, createListenerMiddleware } from "@reduxjs/toolkit";
import { loadState, saveState } from "./localStorage";
import { authSlice } from "./slices/authSlice";
import { bookingSlice } from "./slices/bookingSlice";
import { coreApiSlice } from "./slices/coreApiSlice";
import { outingSlice } from "./slices/outingSlice";
import { reserverDetailsSlice } from "./slices/reserverDetailsSlice";

const listenerMiddleware = createListenerMiddleware();
const reducer = {
  coreApi: coreApiSlice.reducer,
  auth: authSlice.reducer,
  outing: outingSlice.reducer,
  reserverDetails: reserverDetailsSlice.reducer,
  booking: bookingSlice.reducer,
};
const preloadedState = loadState();
const store = configureStore({
  reducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().prepend(listenerMiddleware.middleware).concat(coreApiSlice.middleware),
  preloadedState,
});

// save state on every change, at most once per second
store.subscribe(() => {
  saveState({
    auth: store.getState().auth,
  });
});

export type RootState = StateFromReducersMapObject<typeof reducer>;
export default store;
