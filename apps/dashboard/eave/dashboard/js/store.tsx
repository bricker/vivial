import eventIndexReducer from "$eave-dashboard/js/features/eventIndex/eventIndexSlice";
import { configureStore } from "@reduxjs/toolkit";

export const store = configureStore({
  reducer: {
    eventIndex: eventIndexReducer,
    // other reducers
  },
});

// From Redux's Typescript Documentation:
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;
