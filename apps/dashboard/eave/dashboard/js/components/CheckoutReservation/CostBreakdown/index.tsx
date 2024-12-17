import { Outing, type BookingDetails } from "$eave-dashboard/js/graphql/generated/graphql";
import { currencyFormatter } from "$eave-dashboard/js/util/currency";
import { Divider, Typography, styled } from "@mui/material";
import React from "react";

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

type Breakdown = { costName: string; costValue: string };

/**
 * Build an array of cost breakdowns.
 * @param outing
 * @returns list of objects with named sources of a cost, and the cost as a USD currency string (or "FREE")
 */
function buildBreakdowns(outing: Outing | BookingDetails): Breakdown[] {
  const breakdown: Breakdown[] = [];

  if (outing.restaurant) {
    breakdown.push({
      costName: outing.restaurant.name,
      costValue: currencyFormatter.format(0),
    });
  }

  if (outing.activity?.ticketInfo) {
    const costBreakdown = outing.activity.ticketInfo.costBreakdown;

    breakdown.push({
      costName: outing.activity.name,
      costValue: currencyFormatter.format(costBreakdown.totalCostCents / 100),
    });

    if (costBreakdown.feeCents || costBreakdown.taxCents) {
      const feesCents = costBreakdown.feeCents + costBreakdown.taxCents;

      breakdown.push({
        costName: "3rd party Service Fees & Taxes",
        costValue: currencyFormatter.format(feesCents / 100),
      });
    }
  }

  breakdown.push({
    costName: "Service Fees via Vivial",
    costValue: FREE,
  });

  return breakdown;
}

const CostBreakdown = ({ outing }: { outing: Outing | BookingDetails }) => {
  const totalCostCents = outing.costBreakdown.totalCostCents;
  const totalCostFormatted = currencyFormatter.format(totalCostCents / 100);

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
              <>
                <LineItemText>{charge.costName}</LineItemText>
                <LineItemText>...</LineItemText>
                <LineItemText bold={charge.costValue === FREE}>{charge.costValue}</LineItemText>
              </>
            ))}
          </LineItemContainer>
        </BreakdownContainer>
      </ComponentContainer>
    </>
  );
};

export default CostBreakdown;
