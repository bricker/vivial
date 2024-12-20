import { Outing, type BookingDetails } from "$eave-dashboard/js/graphql/generated/graphql";
import { formatBaseCost, formatFeesAndTaxes, formatTotalCost } from "$eave-dashboard/js/util/currency";
import { Divider, Typography, styled } from "@mui/material";
import React, { Fragment } from "react";

const FREE = "FREE";

const ComponentContainer = styled("div")(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  padding: "24px 32px",
  display: "flex",
  flexDirection: "column",
  gap: 16,
}));

const TotalCostContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-between",
}));

const TopDivider = styled(Divider)(({ theme }) => ({
  borderColor: theme.palette.primary.main,
}));

const CostDivider = styled(Divider)(({ theme }) => ({
  borderColor: theme.palette.grey[800],
}));

const TotalText = styled(Typography)(({ theme }) => ({
  color: theme.palette.common.white,
  fontWeight: 600,
}));

const BreakdownContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "flex-end",
}));

const LineItemContainer = styled("div")(() => ({
  display: "grid",
  gridTemplateColumns: "auto auto auto",
  alignItems: "flex-end",
  textAlign: "right",
  columnGap: 8,
}));

const LineItemText = styled(Typography)<{ bold?: boolean }>(({ bold }) => ({
  fontWeight: bold ? "bold" : "inherit",
}));

type Breakdown = { key: string; costName: string; costValue: string };

/**
 * Build an array of cost breakdowns.
 * @param outing
 * @returns list of objects with named sources of a cost, and the cost as a USD currency string (or "FREE")
 */
function buildBreakdowns(outing: Outing | BookingDetails): Breakdown[] {
  const breakdown: Breakdown[] = [];

  if (outing.reservation) {
    breakdown.push({
      key: "reservation",
      costName: outing.reservation.restaurant.name,
      costValue: formatBaseCost(outing.reservation.costBreakdown),
    });
  }

  if (outing.activityPlan) {
    breakdown.push({
      key: "activity",
      costName: outing.activityPlan.activity.name,
      costValue: formatBaseCost(outing.activityPlan.costBreakdown),
    });
  }

  const feesAndTaxesCents = outing.costBreakdown.feeCents + outing.costBreakdown.taxCents;
  if (feesAndTaxesCents > 0) {
    breakdown.push({
      key: "taxesAndFees",
      costName: "3rd party Service Fees & Taxes",
      costValue: formatFeesAndTaxes(outing.costBreakdown),
    });
  }

  breakdown.push({
    key: "vivialFees",
    costName: "Service Fees via Vivial",
    costValue: FREE,
  });

  return breakdown;
}

const CostBreakdown = ({ outing }: { outing: Outing | BookingDetails }) => {
  const totalCostFormatted = formatTotalCost(outing.costBreakdown);
  const breakdown = buildBreakdowns(outing);

  return (
    <>
      <TopDivider />
      <ComponentContainer>
        <TotalCostContainer>
          <TotalText variant="subtitle2">Total Costs</TotalText>
          <TotalText variant="subtitle2">{totalCostFormatted}</TotalText>
        </TotalCostContainer>
        <CostDivider />
        <BreakdownContainer>
          <LineItemContainer>
            {breakdown.map((charge) => (
              <Fragment key={charge.key}>
                <LineItemText>{charge.costName}</LineItemText>
                <LineItemText>...</LineItemText>
                <LineItemText bold={charge.costValue === FREE}>{charge.costValue}</LineItemText>
              </Fragment>
            ))}
          </LineItemContainer>
        </BreakdownContainer>
      </ComponentContainer>
    </>
  );
};

export default CostBreakdown;
