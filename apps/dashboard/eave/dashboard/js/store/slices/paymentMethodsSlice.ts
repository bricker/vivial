import type { PaymentMethod, PaymentMethodFieldsFragment } from "$eave-dashboard/js/graphql/generated/graphql";
import { createSlice } from "@reduxjs/toolkit";

interface PaymentMethodsState {
  paymentMethods: PaymentMethodFieldsFragment[] | null;
}

const initialState: PaymentMethodsState = {
  paymentMethods: null,
};

export const paymentMethodsSlice = createSlice({
  name: "paymentMethods",
  initialState,
  reducers: {
    storePaymentMethods: (state, action: { payload: { paymentMethods: PaymentMethodFieldsFragment[] } }) => {
      state.paymentMethods = action.payload.paymentMethods;
    },
  },
});

export const { storePaymentMethods } = paymentMethodsSlice.actions;
