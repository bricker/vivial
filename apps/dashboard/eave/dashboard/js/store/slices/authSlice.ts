import { getVisitorId, identify } from "$eave-dashboard/js/analytics/segment";
import { createSlice } from "@reduxjs/toolkit";

interface Account {
  id: string;
  email: string;
}

export interface AuthState {
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
      getVisitorId()
        .then((visitorId) => {
          return identify({
            userId: action.payload.account.id,
            extraProperties: { email: action.payload.account.email, visitorId },
          });
        })
        .catch(() => {
          /* noop ignore analytics errors */
        });
    },
    loggedOut: (state) => {
      state.isLoggedIn = false;
      state.account = null;
    },
    updateEmail: (state, action: { payload: { email: string } }) => {
      if (state.account) {
        state.account.email = action.payload.email;
      }
    },
  },
});

export const { loggedIn, loggedOut, updateEmail } = authSlice.actions;
