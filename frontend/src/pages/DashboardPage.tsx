import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { createAction } from "../api/actions";
import { type DashboardTask, fetchDashboard } from "../api/dashboard";
import { formatDate, formatDaysAgo, todayIsoDate } from "../lib/dates";

type TaskVariant = "overdue" | "due_today" | "needs_attention";

function taskDetail(task: DashboardTask, variant: TaskVariant): string {
  if (task.task === "monitor") {
    if (variant === "needs_attention") {
      if (!task.has_been_monitored) {
        return task.has_monitor_interval
          ? "Needs first monitor"
          : "Needs first monitor · No monitor interval set";
      }
      return "Needs monitor interval";
    }

    if (variant === "overdue") {
      return `Monitor overdue · ${formatDaysAgo(task.due_date)} · due ${formatDate(task.due_date)}`;
    }

    return `Monitor due today · due ${formatDate(task.due_date)}`;
  }

  if (variant === "needs_attention") {
    if (!task.has_been_flushed) {
      return task.has_flush_interval
        ? "Needs first flush"
        : "Needs first flush · No flush interval set";
    }
    return "Needs flush interval";
  }

  if (variant === "overdue") {
    return `Flush overdue · ${formatDaysAgo(task.due_date)} · due ${formatDate(task.due_date)}`;
  }

  return `Flush due today · due ${formatDate(task.due_date)}`;
}

function taskActionLabel(task: DashboardTask): string {
  return task.task === "monitor" ? "Log monitor" : "Log flush";
}

function TaskRow({
  task,
  variant,
  onLogAction,
  isLogging,
}: {
  task: DashboardTask;
  variant: TaskVariant;
  onLogAction: (task: DashboardTask) => void;
  isLogging: boolean;
}) {
  const detail = taskDetail(task, variant);
  return (
    <li className="flex flex-col gap-3 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <Link
          to={`/plants/${task.plant_id}`}
          className="font-medium text-slate-900 hover:text-emerald-700"
        >
          {task.plant_name}
        </Link>
        <p className="mt-1 text-sm text-slate-600">{detail}</p>
      </div>
      <button
        type="button"
        onClick={() => onLogAction(task)}
        disabled={isLogging}
        className="shrink-0 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
      >
        {isLogging ? "Logging..." : taskActionLabel(task)}
      </button>
    </li>
  );
}

function TaskSection({
  title,
  description,
  tasks,
  variant,
  onLogAction,
  loggingPlantId,
}: {
  title: string;
  description: string;
  tasks: DashboardTask[];
  variant: TaskVariant;
  onLogAction: (task: DashboardTask) => void;
  loggingPlantId: number | null;
}) {
  if (tasks.length === 0) {
    return null;
  }

  const borderClass =
    variant === "overdue"
      ? "border-red-200"
      : variant === "needs_attention"
        ? "border-slate-200"
        : "border-amber-200";
  const titleClass =
    variant === "overdue"
      ? "text-red-900"
      : variant === "needs_attention"
        ? "text-slate-800"
        : "text-amber-900";

  return (
    <section className={`rounded-xl border ${borderClass} bg-white shadow-sm`}>
      <div className="border-b border-slate-200 px-6 py-4">
        <h3 className={`text-sm font-semibold uppercase tracking-wide ${titleClass}`}>{title}</h3>
        <p className="mt-1 text-sm text-slate-600">{description}</p>
      </div>
      <ul className="divide-y divide-slate-200">
        {tasks.map((task) => (
          <TaskRow
            key={`${task.plant_id}-${task.task}`}
            task={task}
            variant={variant}
            onLogAction={onLogAction}
            isLogging={loggingPlantId === task.plant_id}
          />
        ))}
      </ul>
    </section>
  );
}

export function DashboardPage() {
  const queryClient = useQueryClient();
  const [loggingPlantId, setLoggingPlantId] = useState<number | null>(null);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["dashboard"],
    queryFn: fetchDashboard,
  });

  const logActionMutation = useMutation({
    mutationFn: (task: DashboardTask) =>
      createAction(task.plant_id, {
        action_type: task.task === "monitor" ? "monitor" : "flush",
        performed_at: todayIsoDate(),
      }),
    onMutate: (task) => {
      setLoggingPlantId(task.plant_id);
    },
    onSuccess: (_action, task) => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["plants"] });
      queryClient.invalidateQueries({ queryKey: ["plants", task.plant_id] });
      queryClient.invalidateQueries({ queryKey: ["plants", task.plant_id, "actions"] });
    },
    onSettled: () => {
      setLoggingPlantId(null);
    },
  });

  const overdue = data?.overdue ?? [];
  const dueToday = data?.due_today ?? [];
  const needsAttention = data?.needs_attention ?? [];
  const isEmpty =
    !isLoading &&
    !isError &&
    overdue.length === 0 &&
    dueToday.length === 0 &&
    needsAttention.length === 0;

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Dashboard</h2>
        <p className="mt-1 text-sm text-slate-600">
          Tasks for your plants and cuttings that are overdue, due today, or still need setup.
        </p>
      </div>

      {isLoading && <p className="text-sm text-slate-600">Loading tasks...</p>}
      {isError && (
        <p className="text-sm text-red-600">Failed to load dashboard. Is the API running?</p>
      )}

      {isEmpty && (
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm text-slate-600">Nothing due today. You&apos;re all caught up.</p>
          <Link to="/plants" className="mt-2 inline-block text-sm font-medium text-emerald-700 hover:underline">
            View plants
          </Link>
        </div>
      )}

      {!isLoading && !isError && (
        <>
          <TaskSection
            title="Overdue"
            description="These tasks were due before today."
            tasks={overdue}
            variant="overdue"
            onLogAction={(task) => logActionMutation.mutate(task)}
            loggingPlantId={loggingPlantId}
          />
          <TaskSection
            title="Due today"
            description="These tasks are due today."
            tasks={dueToday}
            variant="due_today"
            onLogAction={(task) => logActionMutation.mutate(task)}
            loggingPlantId={loggingPlantId}
          />
          <TaskSection
            title="Needs attention"
            description="These plants and cuttings still need a first action or a schedule interval."
            tasks={needsAttention}
            variant="needs_attention"
            onLogAction={(task) => logActionMutation.mutate(task)}
            loggingPlantId={loggingPlantId}
          />
        </>
      )}
    </section>
  );
}
