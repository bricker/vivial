import { getVisitorId, identify, analytics } from "$eave-dashboard/js/analytics/segment";
import type { AccountFieldsFragment } from "$eave-dashboard/js/graphql/generated/graphql";
import { createSlice } from "@reduxjs/toolkit";

export interface AuthState {
  isLoggedIn: boolean | null;
  account: AccountFieldsFragment | null;
}

const initialState: AuthState = {
  isLoggedIn: null,
  account: null,
};

export const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    loggedIn: (state, action: { payload: { account: AccountFieldsFragment } }) => {
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
      analytics.reset().catch((e) => console.error(e));
    },
    updateEmail: (state, action: { payload: { email: string } }) => {
      if (state.account) {
        state.account.email = action.payload.email;
      }
    },
  },
});

export const { loggedIn, loggedOut, updateEmail } = authSlice.actions;
