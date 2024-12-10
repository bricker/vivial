import { type Outing } from "$eave-dashboard/js/graphql/generated/graphql";
import { createSlice } from "@reduxjs/toolkit";

export interface OutingState {
  details: Outing | null;
}

const initialState: OutingState = {
  details: null,
};

export const outingSlice = createSlice({
  name: "outing",
  initialState,
  reducers: {
    plannedOuting: (state, action: { payload: { outing: Outing } }) => {
      state.details = action.payload.outing;
    },
    unsetOuting: (state) => {
      state.details = null;
    },
  },
});

export const { plannedOuting, unsetOuting } = outingSlice.actions;
