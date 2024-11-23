// https://docs.stripe.com/sdks/stripejs-react

import { myWindow } from "$eave-dashboard/js/types/window";
import { Button } from "@mui/material";
import { PaymentElement, useElements, useStripe } from "@stripe/react-stripe-js";
import React, { useCallback } from "react";

const PaymentExamplePage = () => {
  const stripeClient = useStripe();
  const stripeElements = useElements();

  const handleSubmitClick = useCallback(
    async () => {
      if (!stripeClient || !stripeElements) {
        console.warn("stripe not loaded");
        return;
      }

      const response = await stripeClient.confirmPayment({
        elements: stripeElements,
        clientSecret: "", // This property is required but already provided by stripeElements
        confirmParams: {
          return_url: `${myWindow.app.apiBase}/public/stripe/callback`,
        },
      });

      if (response.error) {
        console.error(response.error);
      }
    },
    [stripeClient, stripeElements],
  );

  // Testing? See here: https://docs.stripe.com/testing#cards
  // TL;DR: Number: 4242 4242 4242 4242; Exp: 10/30; Code: 123; Zip: 12345
  return (
    <>
      <PaymentElement options={{}} />
      <Button variant="contained" onClick={handleSubmitClick}>
        Book
      </Button>
    </>
  );
};

export default PaymentExamplePage;
