import { useMutation, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useEffect, useState } from "react";
import { updatePlantSchedule, type ManagedKind, type Plant } from "../api/plants";
import { ScheduleStatusBadge } from "./FlushStatusBadge";
import { formatDate, getScheduleStatus } from "../lib/schedule";

type ScheduleSectionProps = {
  plant: Plant;
};

const SCHEDULE_COPY: Record<
  ManagedKind,
  {
    title: string;
    lastLabel: string;
    nextLabel: string;
    intervalId: string;
    helpText: string;
    lastDate: (plant: Plant) => string | null;
    nextDate: (plant: Plant) => string | null;
    intervalDays: (plant: Plant) => number | null;
    scheduleField: "flush_interval_days" | "monitor_interval_days";
  }
> = {
  semi_hydro: {
    title: "Flush schedule",
    lastLabel: "Last flushed",
    nextLabel: "Next flush",
    intervalId: "flush-interval",
    helpText:
      "Last flushed is taken from your flush actions. Logging a new flush advances the next due date when an interval is set.",
    lastDate: (plant) => plant.last_flush_date,
    nextDate: (plant) => plant.next_flush_date,
    intervalDays: (plant) => plant.flush_interval_days,
    scheduleField: "flush_interval_days",
  },
  cutting: {
    title: "Monitoring schedule",
    lastLabel: "Last monitored",
    nextLabel: "Next monitor",
    intervalId: "monitor-interval",
    helpText:
      "Last monitored is taken from your monitor actions. Logging a new monitor advances the next due date when an interval is set.",
    lastDate: (plant) => plant.last_monitor_date,
    nextDate: (plant) => plant.next_monitor_date,
    intervalDays: (plant) => plant.monitor_interval_days,
    scheduleField: "monitor_interval_days",
  },
};

export function ScheduleSection({ plant }: ScheduleSectionProps) {
  const queryClient = useQueryClient();
  const copy = SCHEDULE_COPY[plant.kind];
  const [intervalDays, setIntervalDays] = useState(
    copy.intervalDays(plant)?.toString() ?? "",
  );
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIntervalDays(copy.intervalDays(plant)?.toString() ?? "");
  }, [plant.kind, plant.flush_interval_days, plant.monitor_interval_days]);

  const mutation = useMutation({
    mutationFn: (schedule: Parameters<typeof updatePlantSchedule>[1]) =>
      updatePlantSchedule(plant.id, schedule),
    onSuccess: (updated) => {
      queryClient.setQueryData(["plants", plant.id], updated);
      queryClient.invalidateQueries({ queryKey: ["plants"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      const updatedCopy = SCHEDULE_COPY[updated.kind];
      setIntervalDays(updatedCopy.intervalDays(updated)?.toString() ?? "");
      setError(null);
    },
    onError: () => setError("Failed to save schedule."),
  });

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();

    const trimmedInterval = intervalDays.trim();
    const payload: Parameters<typeof updatePlantSchedule>[1] = {};

    if (trimmedInterval) {
      const parsed = Number(trimmedInterval);
      if (!Number.isInteger(parsed) || parsed < 1) {
        setError("Interval must be a whole number of at least 1 day.");
        return;
      }
      payload[copy.scheduleField] = parsed;
    } else {
      payload[copy.scheduleField] = null;
    }

    await mutation.mutateAsync(payload);
  }

  const nextDueDate = copy.nextDate(plant);
  const status = getScheduleStatus(nextDueDate);

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          {copy.title}
        </h3>
        <ScheduleStatusBadge kind={plant.kind} nextDueDate={nextDueDate} />
      </div>

      <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-slate-500">{copy.lastLabel}</dt>
          <dd className="font-medium text-slate-900">
            {copy.lastDate(plant) ? formatDate(copy.lastDate(plant)!) : "—"}
          </dd>
        </div>
        <div>
          <dt className="text-slate-500">{copy.nextLabel}</dt>
          <dd className="font-medium text-slate-900">
            {nextDueDate ? (
              <>
                {formatDate(nextDueDate)}
                {status === "overdue" && " (overdue)"}
                {status === "due_today" && " (today)"}
              </>
            ) : (
              "—"
            )}
          </dd>
        </div>
      </dl>

      <form onSubmit={handleSubmit} className="mt-4 space-y-3">
        <div>
          <label htmlFor={copy.intervalId} className="mb-1 block text-sm font-medium text-slate-700">
            Interval (days)
          </label>
          <input
            id={copy.intervalId}
            type="number"
            min={1}
            value={intervalDays}
            onChange={(event) => setIntervalDays(event.target.value)}
            placeholder="e.g. 7"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
          />
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={mutation.isPending}
          className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
        >
          {mutation.isPending ? "Saving..." : "Save interval"}
        </button>
      </form>

      <p className="mt-4 text-xs text-slate-500">{copy.helpText}</p>
    </section>
  );
}
