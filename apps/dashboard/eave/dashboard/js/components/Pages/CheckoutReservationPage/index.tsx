import { AppRoute } from "$eave-dashboard/js/routes";
import React, { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import CheckoutReservation from "../../CheckoutReservation";

const CheckoutReservationPage = () => {
  const navigate = useNavigate();
  const params = useParams();
  const outingId = params["outingId"];

  // validate path param is a UUID
  useEffect(() => {
    // regex from https://stackoverflow.com/a/13653180
    const uuidRegex = new RegExp(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    const possibleUuid = outingId || "";
    if (!outingId || !uuidRegex.test(possibleUuid)) {
      navigate(AppRoute.root);
    }
  }, []);

  return <CheckoutReservation outingId={outingId || ""} showStripeBadge showCostBreakdown />;
};

export default CheckoutReservationPage;
