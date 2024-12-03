import { type SearchRegion } from "$eave-dashboard/js/graphql/generated/graphql";
import { LOCALE, MONTH_DAY_LABELS } from "./constants";

function getTimeOfDay(date: Date): string {
  const formattedDate = date.toLocaleTimeString(LOCALE, {
    hour12: true,
    hour: "numeric",
    minute: "numeric",
  });
  return formattedDate.replace(/ |:00/g, "").toLowerCase(); // 6:00 PM -> 6pm, 6:30 PM -> 6:30pm
}

function getDayOfMonth(date: Date): string {
  return MONTH_DAY_LABELS[date.getDate()] || "";
}

function getShortMonth(date: Date): string {
  return date.toLocaleDateString(LOCALE, { month: "short" });
}

function isTomorrow(startTime: Date): boolean {
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);
  return startTime.toDateString() === tomorrow.toDateString();
}

export function getStartTimeLabel(startTime: Date): string {
  const month = getShortMonth(startTime);
  const dayOfMonth = getDayOfMonth(startTime);
  const timeOfDay = getTimeOfDay(startTime);
  if (isTomorrow(startTime)) {
    return `Tomorrow @ ${timeOfDay}`;
  }
  return `${month} ${dayOfMonth} @ ${timeOfDay}`;
}

export function getSearchAreaLabel(searchAreaIds: string[], searchRegions: SearchRegion[]): string {
  if (searchAreaIds.length === searchRegions.length) {
    return "Anywhere in LA";
  }
  const regionMap: { [key: string]: string } = {};
  let label = "";
  searchRegions.forEach((region) => (regionMap[region.id] = region.name));
  searchAreaIds.forEach((id, i) => {
    const last_i = searchAreaIds.length - 1;
    if (i === last_i) {
      label += regionMap[id];
    } else {
      label += `${regionMap[id]}, `;
    }
  });
  return label;
}
