import { type BookingDetails, type Outing, type OutingPreferences } from "$eave-dashboard/js/graphql/generated/graphql";
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
    openedBookingDetails: (state, action: { payload: { bookingDetails: BookingDetails } }) => {
      state.details = action.payload.bookingDetails as Outing;
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
      if (action.payload.user) {
        state.preferenes.user = action.payload.user;
      }
      if (action.payload.partner) {
        state.preferenes.partner = action.payload.partner;
      }
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

export const { plannedOuting, openedBookingDetails, chosePreferences, unsetOuting } = outingSlice.actions;
