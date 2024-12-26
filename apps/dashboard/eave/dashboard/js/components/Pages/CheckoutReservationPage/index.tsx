import React from "react";
import { useParams } from "react-router-dom";
import CheckoutFormStripeElementsProvider from "../../CheckoutReservation";

const CheckoutReservationPage = () => {
  const params = useParams();
  const outingId = params["outingId"]!;
  return <CheckoutFormStripeElementsProvider outingId={outingId} />
};

export default CheckoutReservationPage;
