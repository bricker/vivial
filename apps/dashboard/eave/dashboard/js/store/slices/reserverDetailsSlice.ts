import { createSlice } from "@reduxjs/toolkit";

interface ReserverDetails {
  id: string;
  firstName: string;
  lastName: string;
  phoneNumber: string;
}

interface AccountReserverDetailsState {
  reserverDetails: ReserverDetails | null;
}

const initialState: AccountReserverDetailsState = {
  reserverDetails: null,
};

export const reserverDetailsSlice = createSlice({
  name: "reserverDetails",
  initialState,
  reducers: {
    storeReserverDetails: (state, action: { payload: { details: ReserverDetails } }) => {
      state.reserverDetails = action.payload.details;
    },
  },
});

export const { storeReserverDetails } = reserverDetailsSlice.actions;
