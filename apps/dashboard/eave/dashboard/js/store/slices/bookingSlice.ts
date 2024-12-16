import { type Booking, type BookingDetails } from "$eave-dashboard/js/graphql/generated/graphql";
import { createSlice } from "@reduxjs/toolkit";

export interface BookingState {
  booking?: Booking;
  bookingDetails?: BookingDetails;
}

const initialState: BookingState = {};

export const bookingSlice = createSlice({
  name: "booking",
  initialState,
  reducers: {
    setBooking: (state, action: { payload: { booking: Booking } }) => {
      state.booking = action.payload.booking;
    },
    setBookingDetails: (state, action: { payload: { bookingDetails: BookingDetails }}) => {
      state.bookingDetails = action.payload.bookingDetails;
    },
  },
});

export const { setBooking, setBookingDetails } = bookingSlice.actions;
