import React from "react";
import { useSearchParams } from "react-router-dom";

const BookingConfirmationPage = () => {
  const [searchParams] = useSearchParams();

  const paymentIntentId = searchParams.get("payment_intent");
  const clientSecret = searchParams.get("payment_intent_client_secret");
  const redirectStatus = searchParams.get("redirect_status");

  return (
    <div>
      BOOKING CONFIRMATION PAGE
      <br />
      id={paymentIntentId}
      <br />
      secret={clientSecret}
      <br />
      status={redirectStatus}
      <br />
    </div>
  );
};

export default BookingConfirmationPage;
