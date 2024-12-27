import { useGetBillingPortalUrlQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import React, { useEffect } from "react";
import CenteringContainer from "../../CenteringContainer";

const StripeCustomerPortal = () => {
  const { data } = useGetBillingPortalUrlQuery({});

  useEffect(() => {
    if (data?.viewer.__typename === "AuthenticatedViewerQueries" && data.viewer.billingPortalUrl) {
      window.location.assign(data.viewer.billingPortalUrl);
    }
  }, [data]);

  // just show loading UI until we can redirect customer to their Stripe portal
  return <CenteringContainer>Redirecting you to Stripe...</CenteringContainer>;
};

export default StripeCustomerPortal;
