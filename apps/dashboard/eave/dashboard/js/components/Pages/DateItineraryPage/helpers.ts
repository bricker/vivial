import { type Outing, type OutingBudget, type Restaurant } from "$eave-dashboard/js/graphql/generated/graphql";
import { imageUrl } from "$eave-dashboard/js/util/asset";
import { getBudgetLabel } from "$eave-dashboard/js/util/budget";
import { getDayOfWeek, getMonth, getTimeOfDay } from "$eave-dashboard/js/util/date";
import { getMultiRegionLabel } from "$eave-dashboard/js/util/region";

export function getTotalCost(outing: Outing | null): string | null {
  if (outing?.activity) {
    const { activity } = outing;
    const ticketInfo = activity.ticketInfo;
    if (ticketInfo) {
      const cost = ticketInfo.cost || 0;
      const fee = ticketInfo.fee || 0;
      const tax = ticketInfo.tax || 0;
      const totalCost = (cost + fee + tax) * outing.survey.headcount;
      if (totalCost) {
        return `$${(totalCost / 100).toFixed(2)}`;
      }
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

export function getRestaurantImgUrls(restaurant: Restaurant): string[] {
  let imgUrls: string[] = [];
  const photos = restaurant?.photos;
  if (photos?.coverPhotoUri) {
    imgUrls.push(photos.coverPhotoUri);
  }
  if (photos?.supplementalPhotoUris) {
    imgUrls = imgUrls.concat(photos.supplementalPhotoUris);
  }
  return imgUrls;
}
