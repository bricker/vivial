import {
  type ActivityCategoryFieldsFragment,
  type ItineraryFieldsFragment,
  type RestaurantCategoryFieldsFragment,
  type TravelFieldsFragment,
} from "$eave-dashboard/js/graphql/generated/graphql";
import { createSlice } from "@reduxjs/toolkit";

export type OutingPreferencesSelections = {
  // Because this is an input, using the Fragment types here isn't technically correct, but close enough.
  restaurantCategories?: RestaurantCategoryFieldsFragment[] | null;
  activityCategories?: ActivityCategoryFieldsFragment[] | null;
};

export interface OutingState {
  details: (ItineraryFieldsFragment & TravelFieldsFragment) | null;
  preferenes: {
    user: OutingPreferencesSelections | null;
    partner: OutingPreferencesSelections | null;
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
    plannedOuting: (state, action: { payload: { outing: ItineraryFieldsFragment & TravelFieldsFragment } }) => {
      state.details = action.payload.outing;
    },
    openedBookingDetails: (state, action: { payload: { bookingDetails: ItineraryFieldsFragment } }) => {
      state.details = action.payload.bookingDetails;
    },
    chosePreferences: (
      state,
      action: {
        payload: {
          user?: OutingPreferencesSelections | null;
          partner?: OutingPreferencesSelections | null;
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
