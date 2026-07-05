import { getFlushStatus } from "../lib/schedule";

export function FlushStatusBadge({ nextFlushDate }: { nextFlushDate: string | null }) {
  const status = getFlushStatus(nextFlushDate);

  if (status === "overdue") {
    return (
      <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800">
        Flush overdue
      </span>
    );
  }

  if (status === "due_today") {
    return (
      <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
        Flush due today
      </span>
    );
  }

  return null;
}
