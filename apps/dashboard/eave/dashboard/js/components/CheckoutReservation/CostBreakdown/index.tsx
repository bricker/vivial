import { ActivitySource, type ItineraryFieldsFragment } from "$eave-dashboard/js/graphql/generated/graphql";
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
 * @param itinerary
 * @returns list of objects with named sources of a cost, and the cost as a USD currency string (or "FREE")
 */
function buildBreakdowns(itinerary: ItineraryFieldsFragment): Breakdown[] {
  const breakdown: Breakdown[] = [];

  if (itinerary.reservation) {
    breakdown.push({
      key: "reservation",
      costName: itinerary.reservation.restaurant.name,
      costValue: formatBaseCost(itinerary.reservation.costBreakdown),
    });
  }

  if (itinerary.activityPlan) {
    breakdown.push({
      key: "activity",
      costName: itinerary.activityPlan.activity.name,
      costValue: formatBaseCost(itinerary.activityPlan.costBreakdown),
    });
  }

  const feesAndTaxesCents = itinerary.costBreakdown.feeCents + itinerary.costBreakdown.taxCents;
  if (feesAndTaxesCents > 0) {
    breakdown.push({
      key: "taxesAndFees",
      costName:
        itinerary.activityPlan?.activity.source === ActivitySource.Eventbrite
          ? "Service Fees & Taxes via Eventbrite"
          : "Service Fees & Taxes",
      costValue: formatFeesAndTaxes(itinerary.costBreakdown),
    });
  }

  breakdown.push({
    key: "vivialFees",
    costName: "Service Fees via Vivial",
    costValue: FREE,
  });

  return breakdown;
}

const CostBreakdown = ({ itinerary }: { itinerary: ItineraryFieldsFragment }) => {
  const totalCostFormatted = formatTotalCost(itinerary.costBreakdown);
  const breakdown = buildBreakdowns(itinerary);

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
