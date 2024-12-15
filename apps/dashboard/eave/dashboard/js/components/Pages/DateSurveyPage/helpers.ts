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
