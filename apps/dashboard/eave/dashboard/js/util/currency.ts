import { type CostBreakdownFieldsFragment, type ItineraryFieldsFragment } from "../graphql/generated/graphql";

export const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

export const ZERO_DOLLARS_FORMATTED = currencyFormatter.format(0);

export function formatTotalCost(costBreakdown: CostBreakdownFieldsFragment): string {
  return currencyFormatter.format(costBreakdown.totalCostCents / 100);
}

export function formatMaxBaseCost(costBreakdown: CostBreakdownFieldsFragment): string {
  return currencyFormatter.format(costBreakdown.maxBaseCostCents / 100);
}

export function formatMinBaseCost(costBreakdown: CostBreakdownFieldsFragment): string {
  return currencyFormatter.format(costBreakdown.minBaseCostCents / 100);
}

export function formatFeesAndTaxes(costBreakdown: CostBreakdownFieldsFragment): string {
  return currencyFormatter.format((costBreakdown.feeCents + costBreakdown.taxCents) / 100);
}

export function hasUnbookableCost(outing: ItineraryFieldsFragment): boolean {
  const hasCost = !!outing.activityPlan?.costBreakdown.totalCostCents;
  const isBookable = !!outing.activityPlan?.activity?.isBookable;
  return hasCost && !isBookable;
}
