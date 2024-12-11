import React from "react";
import { useParams } from "react-router-dom";
import CheckoutReservation from "../../CheckoutReservation";

const CheckoutReservationPage = () => {
  const params = useParams();
  const outingId = params["outingId"];
  // TODO: do something if id is bad

  // TODO: render cost header? opentable footer?
  return <CheckoutReservation outingId={outingId!} />;
};

export default CheckoutReservationPage;
