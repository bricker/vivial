import { PaymentElement } from "@stripe/react-stripe-js";
import React from "react";

const PaymentForm = (options: {
  // paymentDetails?: TODO,
}) => {
  // Testing? See here: https://docs.stripe.com/testing#cards
  // TL;DR: Number: 4242 4242 4242 4242; Exp: 10/30; Code: 123; Zip: 12345
  return <PaymentElement options={{}} />;
};

export default PaymentForm;
