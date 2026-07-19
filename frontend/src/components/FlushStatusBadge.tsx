import type { ManagedKind } from "../api/plants";
import { getScheduleStatus } from "../lib/schedule";

const STATUS_LABELS: Record<
  ManagedKind,
  { overdue: string; dueToday: string }
> = {
  semi_hydro: {
    overdue: "Flush overdue",
    dueToday: "Flush due today",
  },
  cutting: {
    overdue: "Monitor overdue",
    dueToday: "Monitor due today",
  },
};

export function ScheduleStatusBadge({
  kind,
  nextDueDate,
}: {
  kind: ManagedKind;
  nextDueDate: string | null;
}) {
  const status = getScheduleStatus(nextDueDate);
  const labels = STATUS_LABELS[kind];

  if (status === "overdue") {
    return (
      <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800">
        {labels.overdue}
      </span>
    );
  }

  if (status === "due_today") {
    return (
      <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
        {labels.dueToday}
      </span>
    );
  }

  return null;
}

/** @deprecated Use ScheduleStatusBadge */
export function FlushStatusBadge({ nextFlushDate }: { nextFlushDate: string | null }) {
  return <ScheduleStatusBadge kind="semi_hydro" nextDueDate={nextFlushDate} />;
}
