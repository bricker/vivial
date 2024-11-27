import { RootState } from ".";
import { AuthState } from "./slices/authSlice";

const persistedStateKey = "vivial_redux_state";

export function loadState(): RootState | undefined {
  try {
    const serializedState = localStorage.getItem(persistedStateKey);
    if (serializedState === null) {
      return undefined;
    }
    return JSON.parse(serializedState) as RootState;
  } catch {
    return undefined;
  }
}

type PersistedState = { auth: AuthState };

export function saveState(state: PersistedState) {
  try {
    const serializedState = JSON.stringify(state);
    localStorage.setItem(persistedStateKey, serializedState);
  } catch {
    // Ignore write errors.
  }
}
