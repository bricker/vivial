import type { ReserverDetailsFieldsFragment } from "$eave-dashboard/js/graphql/generated/graphql";
import { createSlice } from "@reduxjs/toolkit";

interface AccountReserverDetailsState {
  reserverDetails: ReserverDetailsFieldsFragment | null;
}

const initialState: AccountReserverDetailsState = {
  reserverDetails: null,
};

export const reserverDetailsSlice = createSlice({
  name: "reserverDetails",
  initialState,
  reducers: {
    storeReserverDetails: (state, action: { payload: { details: ReserverDetailsFieldsFragment } }) => {
      state.reserverDetails = action.payload.details;
    },
  },
});

export const { storeReserverDetails } = reserverDetailsSlice.actions;
