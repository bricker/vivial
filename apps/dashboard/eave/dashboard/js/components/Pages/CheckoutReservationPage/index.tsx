import { AppRoute } from "$eave-dashboard/js/routes";
import React, { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import CheckoutReservation from "../../CheckoutReservation";

const CheckoutReservationPage = () => {
  const navigate = useNavigate();
  const params = useParams();
  const outingId = params["outingId"];

  useEffect(() => {
    if (!outingId) {
      navigate(AppRoute.root);
    }
  }, [outingId]);

  if (!outingId) {
    return null;
  }

  return <CheckoutReservation outingId={outingId} showStripeBadge showCostBreakdown />;
};

export default CheckoutReservationPage;
