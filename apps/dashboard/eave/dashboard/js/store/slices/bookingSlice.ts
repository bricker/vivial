import { type Booking, type Outing, type OutingPreferences } from "$eave-dashboard/js/graphql/generated/graphql";
import { createSlice } from "@reduxjs/toolkit";

export interface BookingState {
  booking?: Booking;
}

const initialState: BookingState = {
};

export const bookingSlice = createSlice({
  name: "booking",
  initialState,
  reducers: {
    setBooking: (state, action: { payload: { booking: Booking }}) => {
      state.booking = action.payload.booking
    },
  },
});

export const { setBooking } = bookingSlice.actions;
