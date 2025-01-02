import { type SearchRegion } from "$eave-dashboard/js/graphql/generated/graphql";
import { getDayOfMonth, getDayOfWeek, getMonth, getTimeOfDay, isTomorrow } from "$eave-dashboard/js/util/date";

export function getStartTimeLabel(startTime: Date): string {
  const timeOfDay = getTimeOfDay(startTime);
  if (isTomorrow(startTime)) {
    return `Tomorrow @ ${timeOfDay}`;
  }

  let str = "";
  const dow = getDayOfWeek(startTime);
  const dom = getDayOfMonth(startTime);

  if (dow) {
    str += `${dow}`;
    if (dom) {
      str += ", ";
    }
  }

  if (dom) {
    const month = getMonth(startTime);
    str += `${month} ${dom}`;
  }

  if (str.length > 0) {
    str += " @ ";
  }

  str += timeOfDay;
  return str;
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
