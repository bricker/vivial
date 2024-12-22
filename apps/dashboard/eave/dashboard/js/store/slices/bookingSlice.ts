import type { ItineraryFieldsFragment, TravelFieldsFragment } from "$eave-dashboard/js/graphql/generated/graphql";
import { createSlice } from "@reduxjs/toolkit";

export interface BookingState {
  bookingDetails?: ItineraryFieldsFragment & TravelFieldsFragment;
}

const initialState: BookingState = {};

export const bookingSlice = createSlice({
  name: "booking",
  initialState,
  reducers: {
    setBookingDetails: (
      state,
      action: { payload: { bookingDetails: ItineraryFieldsFragment & TravelFieldsFragment } },
    ) => {
      state.bookingDetails = action.payload.bookingDetails;
    },
  },
});

export const { setBookingDetails } = bookingSlice.actions;
