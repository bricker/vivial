import { styled } from "@mui/material";
import { PaymentElement } from "@stripe/react-stripe-js";
import React from "react";

const PaymentContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 8,
}));

const CollapsingContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 8,
}));

const PaymentForm = () => {
  // Testing? See here: https://docs.stripe.com/testing#cards
  // TL;DR: Number: 4242 4242 4242 4242; Exp: 10/30; Code: 123; Zip: 12345
  return (
    <PaymentContainer>
      <CollapsingContainer>
        <PaymentElement />
      </CollapsingContainer>
    </PaymentContainer>
  );
};

export default PaymentForm;
