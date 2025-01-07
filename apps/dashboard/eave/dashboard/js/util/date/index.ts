import { numWithEnglishSuffix } from "../string";
import { LOCALE } from "./constant";

/**
 * 6:00 PM -> 6pm
 * 6:30 PM -> 6:30pm
 *
 * if stripZeroes:
 * 6:00 PM -> 6:00pm
 * 6:30 PM -> 6:30pm
 */
export function getTimeOfDay(date: Date, stripZeroes: boolean = true): string {
  const formattedDate = date.toLocaleTimeString(LOCALE, {
    hour12: true,
    hour: "numeric",
    minute: "numeric",
  });
  const charsToStrip = stripZeroes ? / |:00/g : / /g;
  return formattedDate.replace(charsToStrip, "").toLowerCase();
}

export function getDayOfMonth(date: Date): string {
  return numWithEnglishSuffix(date.getDate());
}

export function getDayOfWeek(date: Date, format: "short" | "long" = "short"): string {
  return date.toLocaleDateString(LOCALE, { weekday: format });
}

export function getMonth(date: Date, format: "numeric" | "short" | "long" = "short"): string {
  return date.toLocaleDateString(LOCALE, { month: format });
}

export function getDate(date: Date): number | null {
  if (isNaN(date.getDate())) {
    return null;
  }
  return date.getDate();
}

export function isTomorrow(date: Date): boolean {
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);
  return date.toDateString() === tomorrow.toDateString();
}

export function isExpired(date: Date): boolean {
  const now = new Date();
  return date < now;
}

export function in24Hours(): Date {
  const now = new Date();
  const millisecondsIn24Hours = 24 * 60 * 60 * 1000;
  return new Date(now.getTime() + millisecondsIn24Hours);
}

export function in1Year(): Date {
  const oneYearFromNow = new Date();
  oneYearFromNow.setFullYear(oneYearFromNow.getFullYear() + 1);
  return oneYearFromNow;
}
export function getDateTimeLabelAbbreviated(date: Date): string {
  const timeOfDay = getTimeOfDay(date);
  if (isTomorrow(date)) {
    return `Tomorrow @ ${timeOfDay}`;
  }

  const dow = getDayOfWeek(date, "short");
  const month = getMonth(date, "short");
  const dom = getDayOfMonth(date);

  const str = `${dow}, ${month} ${dom} @ ${timeOfDay}`;
  return str;
}

export function getDateTimeLabelExtended(date: Date): string {
  const timeOfDay = getTimeOfDay(date);
  const dow = getDayOfWeek(date, "long");
  const month = getMonth(date, "short");
  const dom = getDayOfMonth(date);

  const str = `${dow}, ${month} ${dom} @ ${timeOfDay}`;
  return str;
}
