import { type Outing, type OutingBudget } from "$eave-dashboard/js/graphql/generated/graphql";
import { imageUrl } from "$eave-dashboard/js/util/asset";
import { getBudgetLabel } from "$eave-dashboard/js/util/budget";
import { currencyFormatter } from "$eave-dashboard/js/util/currency";
import { getDayOfWeek, getMonth, getTimeOfDay } from "$eave-dashboard/js/util/date";
import { getMultiRegionLabel } from "$eave-dashboard/js/util/region";

export function getTotalCost(outing: Outing | null): string | null {
  if (outing?.activity) {
    const { activity } = outing;
    const pricing = activity.pricing;
    const totalCostCents = pricing.totalCostCents;
    if (totalCostCents > 0) {
      return currencyFormatter.format(totalCostCents / 100);
    }
  }
  return null;
}

export function getBackgroundImgUrl(_outing: Outing | null): string {
  // TODO: return different URL based on search area id.
  // NOTE: All of the images already exist in /static/images/regions
  return imageUrl("regions/dtla.png");
}

export function getTimeLabel(startTime: Date): string {
  const weekday = getDayOfWeek(startTime);
  const month = getMonth(startTime);
  const date = startTime.getDate();
  const time = getTimeOfDay(startTime);
  return `${weekday}, ${month} ${date} @${time}`;
}

export function getPlaceLabel(headcount: number, searchAreaIds: string[], budget: OutingBudget): string {
  const regionLabel = getMultiRegionLabel(searchAreaIds);
  const budgetLabel = getBudgetLabel(budget);
  return `For ${headcount} • ${regionLabel} • ${budgetLabel}`;
}
