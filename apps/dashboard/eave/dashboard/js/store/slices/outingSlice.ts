import { type Outing, type OutingPreferences } from "$eave-dashboard/js/graphql/generated/graphql";
import { createSlice } from "@reduxjs/toolkit";

export interface OutingState {
  details: Outing | null;
  preferenes: {
    user: OutingPreferences | null;
    partner: OutingPreferences | null;
  };
}

const initialState: OutingState = {
  details: null,
  preferenes: {
    user: null,
    partner: null,
  },
};

export const outingSlice = createSlice({
  name: "outing",
  initialState,
  reducers: {
    plannedOuting: (state, action: { payload: { outing: Outing } }) => {
      state.details = action.payload.outing;
    },
    chosePreferences: (
      state,
      action: {
        payload: {
          user?: OutingPreferences | null;
          partner?: OutingPreferences | null;
        };
      },
    ) => {
      state.preferenes.user = action.payload.user || null;
      state.preferenes.partner = action.payload.partner || null;
    },
    unsetOuting: (state) => {
      state.details = null;
      state.preferenes = {
        user: null,
        partner: null,
      };
    },
  },
});

export const { plannedOuting, chosePreferences, unsetOuting } = outingSlice.actions;
