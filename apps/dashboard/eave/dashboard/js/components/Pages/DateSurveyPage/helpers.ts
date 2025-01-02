/**
 * Returns 6:00PM on the Saturday nearest to now, that is also
 * at least 24 hours away.
 */
export function getInitialStartTime(): Date {
  const now = new Date();
  const startTime = new Date(now);

  // set startTime to the next saturday 6pm
  const sixPM = 18;
  startTime.setHours(sixPM, 0, 0);

  const SATURDAY = 6;
  const daysUntilSaturday = SATURDAY - now.getDay();
  startTime.setDate(startTime.getDate() + daysUntilSaturday);

  // if <24h until startTime, add 1 week to set startTime to following saturday
  const oneDayInMilis = 24 * 60 * 60 * 1000;
  if (startTime.getTime() - now.getTime() < oneDayInMilis) {
    startTime.setDate(startTime.getDate() + 7);
  }
  return startTime;
}
