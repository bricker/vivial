import { createSlice } from "@reduxjs/toolkit";

interface AuthState {
  isLoggedIn: boolean | null;
  accountId: string | null;
}

const initialState: AuthState = {
  isLoggedIn: null,
  accountId: null,
};

export const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    loggedIn: (state, action: { payload: { accountId: string } }) => {
      state.isLoggedIn = true;
      state.accountId = action.payload.accountId;
    },
    loggedOut: (state) => {
      state.isLoggedIn = false;
      state.accountId = null;
    },
  },
});

export const { loggedIn, loggedOut } = authSlice.actions;
