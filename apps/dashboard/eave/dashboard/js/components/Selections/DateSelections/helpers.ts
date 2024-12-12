import { type SearchRegion } from "$eave-dashboard/js/graphql/generated/graphql";
import { getDayOfMonth, getMonth, getTimeOfDay, isTomorrow } from "$eave-dashboard/js/util/date";

export function getStartTimeLabel(startTime: Date): string {
  const timeOfDay = getTimeOfDay(startTime);
  if (isTomorrow(startTime)) {
    return `Tomorrow @ ${timeOfDay}`;
  }
  return `${getMonth(startTime)} ${getDayOfMonth(startTime)} @ ${timeOfDay}`;
}

export function getSearchAreaLabel(searchAreaIds: string[], searchRegions: SearchRegion[]): string {
  if (searchAreaIds.length === searchRegions.length) {
    return "Anywhere in LA";
  }
  const regionMap: { [key: string]: string } = {};
  let label = "";
  searchRegions.forEach((region) => (regionMap[region.id] = region.name));
  searchAreaIds.forEach((id, i) => {
    label += regionMap[id];
    if (i !== searchAreaIds.length - 1) {
      label += ", ";
    }
  });
  return label;
}
