import { type Outing } from "$eave-dashboard/js/graphql/generated/graphql";

export function getTotalCost(outing: Outing | null): string | null {
  if (outing?.activity) {
    const { headcount, activity } = outing;
    const ticketInfo = activity.ticketInfo;
    if (ticketInfo) {
      const cost = ticketInfo.cost || 0;
      const fee = ticketInfo.fee || 0;
      const tax = ticketInfo.tax || 0;
      const totalCost = (cost + fee + tax) * headcount;
      if (totalCost) {
        return `$${(totalCost / 100).toFixed(2)}`;
      }
    }
  }
  return null;
}
