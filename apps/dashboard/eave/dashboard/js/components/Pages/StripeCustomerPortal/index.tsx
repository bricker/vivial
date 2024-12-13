import { useGetStripePortalQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { CircularProgress } from "@mui/material";
import React, { useEffect } from "react";

const StripeCustomerPortal = () => {
  const { data } = useGetStripePortalQuery({});

  useEffect(() => {
    if (data?.viewer.__typename === "AuthenticatedViewerQueries" && data.viewer.stripePortal.url) {
      window.location.assign(data.viewer.stripePortal.url);
    }
  }, [data]);

  // just show loading UI until we can redirect customer to their Stripe portal
  return <CircularProgress color="secondary" />;
};

export default StripeCustomerPortal;
