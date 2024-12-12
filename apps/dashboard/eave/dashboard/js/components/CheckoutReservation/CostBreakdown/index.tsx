import { Outing } from "$eave-dashboard/js/graphql/generated/graphql";
import { Divider, Typography, styled } from "@mui/material";
import React from "react";

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
  gap: 8,
  justifyContent: "flex-end",
}));

const LineItemContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  alignItems: "flex-end",
}));

const LineItemText = styled(Typography)<{ bold?: boolean }>(({ bold }) => ({
  fontWeight: bold ? "bold" : "inherit",
}));

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

type Breakdown = { chargeName: string[]; costValue: string[] };

/**
 * Build a breakdown to render. Indicies of `chargeName` and `costValue`
 * correspond to each other.
 * @param outing
 * @returns object with named sources of a cost, and the cost as a USD currency string (or "FREE")
 */
function buildBreakdown(outing: Outing): Breakdown {
  const breakdown: Breakdown = {
    chargeName: [],
    costValue: [],
  };

  if (outing.restaurant) {
    breakdown.chargeName.push(outing.restaurant.name);
    breakdown.costValue.push(currencyFormatter.format(0));
  }

  if (outing.activity) {
    breakdown.chargeName.push(outing.activity.name);
    const cost = outing.activity.ticketInfo?.cost || 0;
    breakdown.costValue.push(currencyFormatter.format(cost));

    if (outing.activity.ticketInfo?.fee || outing.activity.ticketInfo?.tax) {
      breakdown.chargeName.push("3rd party Service Fees & Taxes");
      const taxFee = (outing.activity.ticketInfo.fee ?? 0) + (outing.activity.ticketInfo.tax ?? 0);
      breakdown.costValue.push(currencyFormatter.format(taxFee));
    }
  }

  breakdown.chargeName.push("Service Fees via Vivial");
  breakdown.costValue.push("FREE");

  return breakdown;
}

const CostBreakdown = ({ outing }: { outing: Outing }) => {
  const costDetails = outing.activity?.ticketInfo;
  const totalCost = currencyFormatter.format(
    (costDetails?.cost ?? 0) + (costDetails?.fee ?? 0) + (costDetails?.tax ?? 0),
  );
  const breakdown = buildBreakdown(outing);
  return (
    <>
      <TopDivider />
      <ComponentContainer>
        <TotalCostContainer>
          <TotalText variant="subtitle2">Total Costs</TotalText>
          <TotalText variant="subtitle2">{totalCost}</TotalText>
        </TotalCostContainer>
        <CostDivider />
        <BreakdownContainer>
          <LineItemContainer>
            {breakdown.chargeName.map((chargeName) => (
              <LineItemText>{chargeName} ...</LineItemText>
            ))}
          </LineItemContainer>
          <LineItemContainer>
            {breakdown.costValue.map((costValue) => (
              <LineItemText bold={costValue === "FREE"}>{costValue}</LineItemText>
            ))}
          </LineItemContainer>
        </BreakdownContainer>
      </ComponentContainer>
    </>
  );
};

export default CostBreakdown;
