import { StateFromReducersMapObject, configureStore, createListenerMiddleware } from "@reduxjs/toolkit";
import { coreApiSlice } from "./slices/coreApiSlice";

const listenerMiddleware = createListenerMiddleware();
const reducer = {
  coreApi: coreApiSlice.reducer,
};
const store = configureStore({
  reducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().prepend(listenerMiddleware.middleware).concat(coreApiSlice.middleware),
});

export type RootState = StateFromReducersMapObject<typeof reducer>;
export default store;
