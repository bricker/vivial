import ExternalLink from "$eave-dashboard/js/components/Links/ExternalLink";
import { CostBreakdown } from "$eave-dashboard/js/graphql/generated/graphql";
import { Button, CircularProgress } from "@mui/material";
import React from "react";

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

function formatCents(cents: number): string {
  return currencyFormatter.format(cents / 100);
}

const CostBreakdownView = ({
  data,
  stripePaymentIntentId,
  bookingState,
  isLoading,
}: {
  data: CostBreakdown | undefined;
  stripePaymentIntentId: string | undefined | null;
  bookingState: string | undefined | null;
  isLoading: boolean;
}) => {
  return (
    <div>
      <h2>Cost info:</h2>
      {isLoading ? (
        <CircularProgress />
      ) : (
        <div>
          <b>Booking State: {bookingState}</b>
          <p>Event costs: {formatCents(data?.baseCostCents || 0)}</p>
          <p>Taxes: {formatCents(data?.taxCents || 0)}</p>
          <p>Fees: {formatCents(data?.feeCents || 0)}</p>
          <b>TOTAL: {formatCents(data?.totalCostCents || 0)}</b>

          <p>
            {stripePaymentIntentId ? (
              <ExternalLink to={`https://dashboard.stripe.com/payments/${stripePaymentIntentId}`}>
                <Button variant="contained">Accept payment on Stripe</Button>
              </ExternalLink>
            ) : (
              "[No stripe payment intent found]"
            )}
          </p>
        </div>
      )}
    </div>
  );
};

export default CostBreakdownView;
