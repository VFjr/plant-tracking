import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useEffect, useState } from "react";
import {
  ACTION_TYPE_LABELS,
  ACTION_TYPES_BY_KIND,
  DEFAULT_ACTION_TYPE_BY_KIND,
  type ActionType,
  createAction,
  deleteAction,
  fetchActions,
} from "../api/actions";
import type { ManagedKind } from "../api/plants";
import { formatDate, todayIsoDate } from "../lib/dates";

type ActionLogSectionProps = {
  plantId: number;
  kind: ManagedKind;
};

export function ActionLogSection({ plantId, kind }: ActionLogSectionProps) {
  const queryClient = useQueryClient();
  const allowedActionTypes = ACTION_TYPES_BY_KIND[kind];
  const [actionType, setActionType] = useState<ActionType>(DEFAULT_ACTION_TYPE_BY_KIND[kind]);
  const [performedAt, setPerformedAt] = useState(todayIsoDate());
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setActionType(DEFAULT_ACTION_TYPE_BY_KIND[kind]);
  }, [kind]);

  const { data: actions, isLoading, isError } = useQuery({
    queryKey: ["plants", plantId, "actions"],
    queryFn: () => fetchActions(plantId),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createAction(plantId, {
        action_type: actionType,
        performed_at: performedAt,
        notes: notes.trim() || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["plants", plantId, "actions"] });
      queryClient.invalidateQueries({ queryKey: ["plants", plantId] });
      queryClient.invalidateQueries({ queryKey: ["plants"] });
      setNotes("");
      setError(null);
    },
    onError: () => setError("Failed to log action."),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["plants", plantId, "actions"] });
      queryClient.invalidateQueries({ queryKey: ["plants", plantId] });
      queryClient.invalidateQueries({ queryKey: ["plants"] });
    },
  });

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!performedAt) {
      setError("Date is required.");
      return;
    }
    await createMutation.mutateAsync();
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Action log</h3>

      <form onSubmit={handleSubmit} className="mt-4 grid gap-3 sm:grid-cols-2">
        <div>
          <label htmlFor="action-type" className="mb-1 block text-sm font-medium text-slate-700">
            Action
          </label>
          <select
            id="action-type"
            value={actionType}
            onChange={(event) => setActionType(event.target.value as ActionType)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
          >
            {allowedActionTypes.map((type) => (
              <option key={type} value={type}>
                {ACTION_TYPE_LABELS[type]}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="performed-at" className="mb-1 block text-sm font-medium text-slate-700">
            Date
          </label>
          <input
            id="performed-at"
            type="date"
            value={performedAt}
            onChange={(event) => setPerformedAt(event.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
            required
          />
        </div>
        <div className="sm:col-span-2">
          <label htmlFor="action-notes" className="mb-1 block text-sm font-medium text-slate-700">
            Notes (optional)
          </label>
          <input
            id="action-notes"
            type="text"
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
          />
        </div>
        {error && (
          <p className="text-sm text-red-600 sm:col-span-2">
            {error}
          </p>
        )}
        <div className="sm:col-span-2">
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
          >
            {createMutation.isPending ? "Logging..." : "Log action"}
          </button>
        </div>
      </form>

      <div className="mt-6">
        {isLoading && <p className="text-sm text-slate-600">Loading actions...</p>}
        {isError && <p className="text-sm text-red-600">Failed to load actions.</p>}
        {!isLoading && !isError && actions?.length === 0 && (
          <p className="text-sm text-slate-600">No actions logged yet.</p>
        )}
        {!isLoading && !isError && actions && actions.length > 0 && (
          <ul className="divide-y divide-slate-200 border-t border-slate-200">
            {actions.map((action) => (
              <li key={action.id} className="flex items-start justify-between gap-4 py-4">
                <div>
                  <p className="text-sm font-medium text-slate-900">
                    {ACTION_TYPE_LABELS[action.action_type]}
                  </p>
                  <p className="mt-1 text-sm text-slate-600">{formatDate(action.performed_at)}</p>
                  {action.notes && <p className="mt-1 text-sm text-slate-600">{action.notes}</p>}
                </div>
                <button
                  type="button"
                  onClick={() => {
                    if (window.confirm("Delete this action?")) {
                      deleteMutation.mutate(action.id);
                    }
                  }}
                  className="shrink-0 text-xs font-medium text-red-700 hover:underline"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
