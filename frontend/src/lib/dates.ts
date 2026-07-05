/** Parse API date or datetime strings without timezone day-shift on YYYY-MM-DD. */
function parseDateValue(value: string): Date {
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split("-").map(Number);
    return new Date(year, month - 1, day);
  }
  return new Date(value);
}

/** Display as day/month/year (e.g. 4/7/2026). */
export function formatDate(value: string): string {
  const date = parseDateValue(value);
  return `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()}`;
}

/** Display date as day/month/year with time (e.g. 4/7/2026, 15:30). */
export function formatDateTime(value: string): string {
  const date = new Date(value);
  const hours = date.getHours().toString().padStart(2, "0");
  const minutes = date.getMinutes().toString().padStart(2, "0");
  return `${formatDate(value)}, ${hours}:${minutes}`;
}

/** ISO date string for today — used for API payloads and comparisons. */
export function todayIsoDate(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = (now.getMonth() + 1).toString().padStart(2, "0");
  const day = now.getDate().toString().padStart(2, "0");
  return `${year}-${month}-${day}`;
}

/** Whole days from an earlier date to a later one (defaults to today). */
export function daysSince(isoDate: string, referenceIso: string = todayIsoDate()): number {
  const from = parseDateValue(isoDate);
  const to = parseDateValue(referenceIso);
  const msPerDay = 24 * 60 * 60 * 1000;
  return Math.round((to.getTime() - from.getTime()) / msPerDay);
}

/** e.g. "1 day ago" or "18 days ago". */
export function formatDaysAgo(isoDate: string, referenceIso?: string): string {
  const days = daysSince(isoDate, referenceIso);
  return days === 1 ? "1 day ago" : `${days} days ago`;
}
