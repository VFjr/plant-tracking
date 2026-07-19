import { todayIsoDate } from "./dates";

export type ScheduleStatus = "overdue" | "due_today" | null;

export { formatDate, formatDateTime, todayIsoDate } from "./dates";

export function getScheduleStatus(nextDueDate: string | null | undefined): ScheduleStatus {
  if (!nextDueDate) {
    return null;
  }

  const today = todayIsoDate();
  if (nextDueDate < today) {
    return "overdue";
  }
  if (nextDueDate === today) {
    return "due_today";
  }
  return null;
}

/** @deprecated Use getScheduleStatus */
export function getFlushStatus(nextFlushDate: string | null | undefined): ScheduleStatus {
  return getScheduleStatus(nextFlushDate);
}

/** @deprecated Use getScheduleStatus */
export function getMonitorStatus(nextMonitorDate: string | null | undefined): ScheduleStatus {
  return getScheduleStatus(nextMonitorDate);
}
