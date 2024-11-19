import React from "react";
import { useSearchParams } from "react-router-dom";

const BookingConfirmationPage = () => {
  const [searchParams] = useSearchParams();

  const paymentIntent = searchParams.get("payment_intent");
  const paymentIntentClientSecret = searchParams.get("payment_intent_client_secret");
  const redirectStatus = searchParams.get("redirect_status");

  console.debug({
    paymentIntent,
    paymentIntentClientSecret,
    redirectStatus,
  });

  // TODO: Probably send a request to the core API with the payment status, and attach it to the booking.

  return <div>BOOKING CONFIRMATION PAGE</div>;
};

export default BookingConfirmationPage;
