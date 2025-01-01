import { type CostBreakdownFieldsFragment, type ItineraryFieldsFragment } from "../graphql/generated/graphql";

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

export const ZERO_DOLLARS_FORMATTED = currencyFormatter.format(0);

export function formatTotalCost(costBreakdown: CostBreakdownFieldsFragment): string {
  return currencyFormatter.format(costBreakdown.totalCostCents / 100);
}

/**
 * Format only the maximum base cost from the costbreakdown object.
 * In most cases, the max cost is the only one we're interested in,
 * even if the minimum cost is different from the max cost at all.
 * @param costBreakdown
 * @returns formatted currency string
 */
export function formatMaxBaseCost(costBreakdown: CostBreakdownFieldsFragment): string {
  return currencyFormatter.format(costBreakdown.maxBaseCostCents / 100);
}

export function formatCostRange(costBreakdown: CostBreakdownFieldsFragment): string {
  const rangeFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
    minimumFractionDigits: 0,
  });
  return `${rangeFormatter.format(costBreakdown.minBaseCostCents / 100)}-${rangeFormatter.format(
    costBreakdown.maxBaseCostCents / 100,
  )}`;
}

export function formatFeesAndTaxes(costBreakdown: CostBreakdownFieldsFragment): string {
  return currencyFormatter.format((costBreakdown.feeCents + costBreakdown.taxCents) / 100);
}

export function hasUnbookableCost(outing: ItineraryFieldsFragment): boolean {
  const hasCost = !!outing.activityPlan?.costBreakdown.totalCostCents;
  const isBookable = !!outing.activityPlan?.activity?.isBookable;
  return hasCost && !isBookable;
}
