import { createSlice } from "@reduxjs/toolkit";

interface Account {
  id: string;
  email: string;
}

interface AuthState {
  isLoggedIn: boolean | null;
  account: Account | null;
}

const initialState: AuthState = {
  isLoggedIn: null,
  account: null,
};

export const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    loggedIn: (state, action: { payload: { account: Account } }) => {
      state.isLoggedIn = true;
      state.account = action.payload.account;
    },
    loggedOut: (state) => {
      state.isLoggedIn = false;
      state.account = null;
    },
    updateEmail: (state, action: { payload: { email: string } }) => {
      if (state.account) {
        state.account = {
          ...state.account,
          email: action.payload.email,
        };
      }
    },
  },
});

export const { loggedIn, loggedOut, updateEmail } = authSlice.actions;
