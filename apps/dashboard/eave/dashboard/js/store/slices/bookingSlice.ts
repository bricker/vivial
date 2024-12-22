import type { BookingDetails } from "$eave-dashboard/js/graphql/generated/graphql";
import { createSlice } from "@reduxjs/toolkit";

export interface BookingState {
  bookingDetails?: BookingDetails;
}

const initialState: BookingState = {};

export const bookingSlice = createSlice({
  name: "booking",
  initialState,
  reducers: {
    setBookingDetails: (state, action: { payload: { bookingDetails: BookingDetails } }) => {
      state.bookingDetails = action.payload.bookingDetails;
    },
  },
});

export const { setBookingDetails } = bookingSlice.actions;
