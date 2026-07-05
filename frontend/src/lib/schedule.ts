import { todayIsoDate } from "./dates";

export type FlushStatus = "overdue" | "due_today" | null;

export { formatDate, formatDateTime, todayIsoDate } from "./dates";

export function getFlushStatus(nextFlushDate: string | null | undefined): FlushStatus {
  if (!nextFlushDate) {
    return null;
  }

  const today = todayIsoDate();
  if (nextFlushDate < today) {
    return "overdue";
  }
  if (nextFlushDate === today) {
    return "due_today";
  }
  return null;
}
