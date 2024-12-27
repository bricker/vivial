const timeFormatter = new Intl.DateTimeFormat("en-US", {
  weekday: "short",
  month: "short",
  day: "numeric",
  year: "numeric",
  hour: "numeric",
  minute: "2-digit",
  hour12: true,
});

export function formatDate(dateString?: string | Date | null): string {
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

export function enumTypeFromValue<T extends object>(target: T, value: string): T[keyof T] | null {
  for (const [k, v] of Object.entries(target)) {
    if (v === value) {
      return target[k as keyof T];
    }
  }
  return null;
}

export function enumKeyFromType<T extends object>(target: T, value: T[keyof T]): keyof T | null {
  return Object.entries(target).find(([_, v]) => v === value)?.[0] as keyof T | null;
}
