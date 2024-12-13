import { LOCALE, MONTH_DAY_LABELS, WEEKDAY_LABELS } from "./constant";

export function getTimeOfDay(date: Date): string {
  const formattedDate = date.toLocaleTimeString(LOCALE, {
    hour12: true,
    hour: "numeric",
    minute: "numeric",
  });
  return formattedDate.replace(/ |:00/g, "").toLowerCase(); // 6:00 PM -> 6pm, 6:30 PM -> 6:30pm
}

export function getDayOfMonth(date: Date): string {
  return MONTH_DAY_LABELS[date.getDate()] || "";
}

export function getDayOfWeek(date: Date): string {
  return WEEKDAY_LABELS[date.getDay()] || "";
}

export function getMonth(date: Date): string {
  return date.toLocaleDateString(LOCALE, { month: "short" });
}

export function isTomorrow(date: Date): boolean {
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);
  return date.toDateString() === tomorrow.toDateString();
}
