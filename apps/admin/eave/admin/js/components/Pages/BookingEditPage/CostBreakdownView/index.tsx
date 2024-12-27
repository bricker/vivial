import ExternalLink from "$eave-dashboard/js/components/Links/ExternalLink";
import Paper from "$eave-dashboard/js/components/Paper";
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
  multiplier,
}: {
  data: CostBreakdown | undefined;
  stripePaymentIntentId: string | undefined | null;
  bookingState: string | undefined | null;
  isLoading: boolean;
  multiplier: number;
}) => {
  const eventCost = (data?.baseCostCents || 0) * multiplier;
  const taxesCost = (data?.taxCents || 0) * multiplier;
  const feesCost = (data?.feeCents || 0) * multiplier;
  const totalCost = (data?.totalCostCents || 0) * multiplier;
  return (
    <Paper>
      <h2>Cost info:</h2>
      {isLoading ? (
        <CircularProgress />
      ) : (
        <div>
          <b>Booking State: {bookingState}</b>
          <p>Event costs: {formatCents(eventCost)}</p>
          <p>Taxes: {formatCents(taxesCost)}</p>
          <p>Fees: {formatCents(feesCost)}</p>
          <b>TOTAL: {formatCents(totalCost)}</b>

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
    </Paper>
  );
};

export default CostBreakdownView;
