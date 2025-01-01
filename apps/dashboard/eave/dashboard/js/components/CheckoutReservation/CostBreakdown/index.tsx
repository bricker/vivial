import { ActivitySource, type ItineraryFieldsFragment } from "$eave-dashboard/js/graphql/generated/graphql";
import {
  ZERO_DOLLARS_FORMATTED,
  formatCostRange,
  formatFeesAndTaxes,
  formatMaxBaseCost,
  formatTotalCost,
  hasUnbookableCost,
} from "$eave-dashboard/js/util/currency";
import { Divider, Typography, styled } from "@mui/material";
import React, { Fragment } from "react";

const FREE = "FREE";

const ComponentContainer = styled("div")(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  display: "flex",
  flexDirection: "column",
  gap: 16,
}));

const TotalCostContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-between",
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

const LineItemText = styled(Typography)<{ boldText?: boolean }>(({ boldText }) => ({
  fontWeight: boldText ? "bold" : "inherit",
}));

type Breakdown = { key: string; costName: string; costValue: string };

/**
 * Build an array of cost breakdowns.
 * @param itinerary
 * @returns list of objects with named sources of a cost, and the cost as a USD currency string (or "FREE")
 */
function buildBreakdowns(itinerary: ItineraryFieldsFragment): Breakdown[] {
  const breakdown: Breakdown[] = [];

  if (itinerary.reservation?.restaurant.reservable) {
    breakdown.push({
      key: "reservation",
      costName: itinerary.reservation.restaurant.name,
      costValue: formatMaxBaseCost(itinerary.reservation.costBreakdown),
    });
  }

  if (itinerary.activityPlan && itinerary.activityPlan.activity.source !== ActivitySource.GooglePlaces) {
    let costValue = formatMaxBaseCost(itinerary.activityPlan.costBreakdown);
    if (
      !itinerary.activityPlan.activity.isBookable &&
      itinerary.activityPlan.costBreakdown.minBaseCostCents !== itinerary.activityPlan.costBreakdown.maxBaseCostCents
    ) {
      costValue = formatCostRange(itinerary.activityPlan.costBreakdown);
    }
    breakdown.push({
      key: "activity",
      costName: itinerary.activityPlan.activity.name,
      costValue,
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
  const breakdown = buildBreakdowns(itinerary);
  const isUnbookable = hasUnbookableCost(itinerary);
  const costHeader = isUnbookable ? "Due Today" : "Total Costs";
  const totalCostFormatted = isUnbookable ? ZERO_DOLLARS_FORMATTED : formatTotalCost(itinerary.costBreakdown);

  return (
    <ComponentContainer>
      <TotalCostContainer>
        <TotalText variant="subtitle2">{costHeader}</TotalText>
        <TotalText variant="subtitle2">{totalCostFormatted}</TotalText>
      </TotalCostContainer>
      <CostDivider />
      <BreakdownContainer>
        <LineItemContainer>
          {breakdown.map((charge) => (
            <Fragment key={charge.key}>
              <LineItemText>{charge.costName}</LineItemText>
              <LineItemText>...</LineItemText>
              <LineItemText boldText={charge.costValue === FREE}>{charge.costValue}</LineItemText>
            </Fragment>
          ))}
        </LineItemContainer>
      </BreakdownContainer>
    </ComponentContainer>
  );
};

export default CostBreakdown;
