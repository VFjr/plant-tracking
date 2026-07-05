import { useMutation, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useEffect, useState } from "react";
import { updatePlantSchedule, type Plant } from "../api/plants";
import { FlushStatusBadge } from "./FlushStatusBadge";
import { formatDate, getFlushStatus } from "../lib/schedule";

type ScheduleSectionProps = {
  plant: Plant;
};

export function ScheduleSection({ plant }: ScheduleSectionProps) {
  const queryClient = useQueryClient();
  const [intervalDays, setIntervalDays] = useState(
    plant.flush_interval_days?.toString() ?? "",
  );
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIntervalDays(plant.flush_interval_days?.toString() ?? "");
  }, [plant.flush_interval_days]);

  const mutation = useMutation({
    mutationFn: (schedule: Parameters<typeof updatePlantSchedule>[1]) =>
      updatePlantSchedule(plant.id, schedule),
    onSuccess: (updated) => {
      queryClient.setQueryData(["plants", plant.id], updated);
      queryClient.invalidateQueries({ queryKey: ["plants"] });
      setIntervalDays(updated.flush_interval_days?.toString() ?? "");
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
      payload.flush_interval_days = parsed;
    } else {
      payload.flush_interval_days = null;
    }

    await mutation.mutateAsync(payload);
  }

  const status = getFlushStatus(plant.next_flush_date);

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Flush schedule
        </h3>
        <FlushStatusBadge nextFlushDate={plant.next_flush_date} />
      </div>

      <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-slate-500">Last flushed</dt>
          <dd className="font-medium text-slate-900">
            {plant.last_flush_date ? formatDate(plant.last_flush_date) : "—"}
          </dd>
        </div>
        <div>
          <dt className="text-slate-500">Next flush</dt>
          <dd className="font-medium text-slate-900">
            {plant.next_flush_date ? (
              <>
                {formatDate(plant.next_flush_date)}
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
          <label htmlFor="flush-interval" className="mb-1 block text-sm font-medium text-slate-700">
            Interval (days)
          </label>
          <input
            id="flush-interval"
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

      <p className="mt-4 text-xs text-slate-500">
        Last flushed is taken from your flush actions. Logging a new flush advances the next due
        date when an interval is set.
      </p>
    </section>
  );
}
