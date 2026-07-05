import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import { createNote, deleteNote, fetchNotes } from "../api/notes";

function formatDateTime(value: string) {
  return new Date(value).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

type NotesSectionProps = {
  plantId: number;
};

export function NotesSection({ plantId }: NotesSectionProps) {
  const queryClient = useQueryClient();
  const [content, setContent] = useState("");
  const [error, setError] = useState<string | null>(null);

  const { data: notes, isLoading, isError } = useQuery({
    queryKey: ["plants", plantId, "notes"],
    queryFn: () => fetchNotes(plantId),
  });

  const createMutation = useMutation({
    mutationFn: (noteContent: string) => createNote(plantId, { content: noteContent }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plants", plantId, "notes"] });
      setContent("");
      setError(null);
    },
    onError: () => setError("Failed to add note."),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteNote,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plants", plantId, "notes"] });
    },
  });

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!content.trim()) {
      setError("Note cannot be empty.");
      return;
    }
    await createMutation.mutateAsync(content.trim());
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Notes</h3>

      <form onSubmit={handleSubmit} className="mt-4 space-y-3">
        <textarea
          value={content}
          onChange={(event) => setContent(event.target.value)}
          rows={3}
          placeholder="Add a note about this plant..."
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={createMutation.isPending}
          className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
        >
          {createMutation.isPending ? "Adding..." : "Add note"}
        </button>
      </form>

      <div className="mt-6">
        {isLoading && <p className="text-sm text-slate-600">Loading notes...</p>}
        {isError && <p className="text-sm text-red-600">Failed to load notes.</p>}
        {!isLoading && !isError && notes?.length === 0 && (
          <p className="text-sm text-slate-600">No notes yet.</p>
        )}
        {!isLoading && !isError && notes && notes.length > 0 && (
          <ul className="divide-y divide-slate-200 border-t border-slate-200">
            {notes.map((note) => (
              <li key={note.id} className="flex items-start justify-between gap-4 py-4">
                <div>
                  <p className="text-sm text-slate-900">{note.content}</p>
                  <p className="mt-1 text-xs text-slate-500">{formatDateTime(note.created_at)}</p>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    if (window.confirm("Delete this note?")) {
                      deleteMutation.mutate(note.id);
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
