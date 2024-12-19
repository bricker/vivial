const timeFormatter = new Intl.DateTimeFormat("en-US", {
  weekday: "short",
  month: "short",
  day: "numeric",
  year: "numeric",
  hour: "numeric",
  minute: "2-digit",
  hour12: true,
});

export function formatDateString(dateString?: string | null): string {
  if (!dateString) {
    return "N/A";
  }
  try {
    const date = new Date(dateString);
    return timeFormatter.format(date);
  } catch {
    return "[invalid date]";
  }
}
