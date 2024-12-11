import React from "react";
import { useParams } from "react-router-dom";
import CheckoutReservation from "../../CheckoutReservation";

const CheckoutReservationPage = () => {
  const params = useParams();
  const outingId = params["outingId"];
  // TODO: do something if id is bad

  return <CheckoutReservation outingId={outingId!} showStripeBadge />;
};

export default CheckoutReservationPage;
