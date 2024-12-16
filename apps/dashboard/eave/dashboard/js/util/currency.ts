import { type Outing } from "../graphql/generated/graphql";

export const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

export function getTotalCost(outing: Outing | null): string {
  if (outing) {
    const totalCostCents = outing.costBreakdown.totalCostCents;
    if (totalCostCents > 0) {
      return currencyFormatter.format(totalCostCents / 100);
    }
  }
  return "$0.00";
}

export function getBaseCost(outing: Outing | null): string {
  if (outing) {
    const baseCostCents = outing.costBreakdown.baseCostCents;
    if (baseCostCents > 0) {
      return currencyFormatter.format(baseCostCents / 100);
    }
  }
  return "$0.00";
}

export function getFees(outing: Outing | null): string {
  if (outing) {
    const fees = outing.costBreakdown.feeCents;
    const taxes = outing.costBreakdown.taxCents;
    if (fees + taxes > 0) {
      return currencyFormatter.format((fees + taxes) / 100);
    }
  }
  return "$0.00";
}
