import {
  ActivitySource,
  type Activity,
  type Outing,
  type OutingBudget,
  type Photos,
} from "$eave-dashboard/js/graphql/generated/graphql";
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

export function getTicketInfo(outing: Outing): string {
  const activity = outing.activityPlan?.activity;
  if (activity) {
    if (activity.source === ActivitySource.Eventbrite) {
      return `${outing.headcount} Tickets`;
    }
    if (activity.source === ActivitySource.GooglePlaces) {
      const primaryTypeName = activity.primaryTypeName?.toLocaleLowerCase();
      if (primaryTypeName?.includes("bar")) {
        return "Drinks";
      }
      if (primaryTypeName?.includes("ice cream")) {
        return "Dessert";
      }
    }
  }
  return "Activity";
}

export function getActivityCategoryInfo(activity: Activity): string {
  if (activity.primaryTypeName) {
    return activity.primaryTypeName;
  }
  if (activity.categoryGroup?.name) {
    return activity.categoryGroup.name;
  }
  return "";
}

export function getActivityVenueName(activity: Activity): string {
  if (activity.source !== ActivitySource.GooglePlaces) {
    return activity.venue.name;
  }
  return "";
}
