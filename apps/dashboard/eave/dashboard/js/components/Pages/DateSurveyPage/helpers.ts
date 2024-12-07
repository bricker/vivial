import { type OutingPreferences } from "$eave-dashboard/js/graphql/generated/graphql";

/**
 * If it's before 6:00 PM at the time that this function is called,
 * this function returns 6:00 PM the next day.
 *
 * Otherwise, this function returns 6:00 PM two days from the currrent day.
 */
export function getInitialStartTime(): Date {
  const now = new Date();
  const startTime = new Date(now);
  const sixPM = 18;
  startTime.setHours(sixPM, 0, 0);
  if (now.getHours() < sixPM) {
    startTime.setDate(now.getDate() + 1);
  } else {
    startTime.setDate(now.getDate() + 2);
  }
  return startTime;
}

export function getHoursDiff(date1: Date, date2: Date): number {
  const msDiff = Math.abs(date1.getTime() - date2.getTime());
  return msDiff / (1000 * 60 * 60);
}

export function getGroupPreferences(
  userPreferences: OutingPreferences | null,
  partnerPreferenecs: OutingPreferences | null,
): OutingPreferences[] {
  if (userPreferences && partnerPreferenecs) {
    return [userPreferences, partnerPreferenecs];
  }
  if (userPreferences) {
    return [userPreferences];
  }
  if (partnerPreferenecs) {
    return [partnerPreferenecs];
  }

  // TODO: Return defaults
  return [];
}
