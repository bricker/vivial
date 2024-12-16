import { type OutingBudget, type Photos } from "$eave-dashboard/js/graphql/generated/graphql";
import { getBudgetLabel } from "$eave-dashboard/js/util/budget";
import { getDayOfWeek, getMonth, getTimeOfDay } from "$eave-dashboard/js/util/date";
import { getMultiRegionLabel } from "$eave-dashboard/js/util/region";

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

export function getImgUrls(photos: Photos): string[] {
  let imgUrls: string[] = [];

  if (!photos) {
    return imgUrls;
  }

  if (photos.coverPhoto) {
    imgUrls.push(photos.coverPhoto.src);
  }

  imgUrls = imgUrls.concat(photos.supplementalPhotos.map((p) => p.src));
  return imgUrls;
}
