import { Typography, styled } from "@mui/material";
import { PaymentElement } from "@stripe/react-stripe-js";
import React from "react";

const PaymentContainer = styled("div")(() => ({}));

const PaymentForm = (options: {
  // paymentDetails?: TODO,
}) => {
  // Testing? See here: https://docs.stripe.com/testing#cards
  // TL;DR: Number: 4242 4242 4242 4242; Exp: 10/30; Code: 123; Zip: 12345
  return (
    <PaymentContainer>
      <Typography variant="subtitle2">Payment information</Typography>
      <PaymentElement options={{}} />
    </PaymentContainer>
  );
};

export default PaymentForm;
