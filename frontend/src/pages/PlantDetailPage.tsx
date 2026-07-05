import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { deletePlant, fetchPlant, updatePlant } from "../api/plants";
import { PlantForm } from "../components/PlantForm";

function formatDate(value: string) {
  return new Date(value).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function wasUpdated(createdAt: string, updatedAt: string) {
  return new Date(updatedAt).getTime() !== new Date(createdAt).getTime();
}

export function PlantDetailPage() {
  const { id } = useParams();
  const plantId = Number(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const { data: plant, isLoading, isError } = useQuery({
    queryKey: ["plants", plantId],
    queryFn: () => fetchPlant(plantId),
    enabled: Number.isFinite(plantId),
  });

  const updateMutation = useMutation({
    mutationFn: (values: Parameters<typeof updatePlant>[1]) => updatePlant(plantId, values),
    onSuccess: (updated) => {
      queryClient.setQueryData(["plants", plantId], updated);
      queryClient.invalidateQueries({ queryKey: ["plants"] });
      setIsEditing(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deletePlant(plantId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plants"] });
      navigate("/plants");
    },
    onError: () => {
      setDeleteError("Failed to delete plant. Please try again.");
    },
  });

  if (!Number.isFinite(plantId)) {
    return <p className="text-sm text-red-600">Invalid plant id.</p>;
  }

  if (isLoading) {
    return <p className="text-sm text-slate-600">Loading plant...</p>;
  }

  if (isError || !plant) {
    return (
      <div className="space-y-3">
        <p className="text-sm text-red-600">Plant not found.</p>
        <Link to="/plants" className="text-sm font-medium text-emerald-700 hover:underline">
          Back to plants
        </Link>
      </div>
    );
  }

  return (
    <section className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <Link to="/plants" className="text-sm font-medium text-emerald-700 hover:underline">
            ← Back to plants
          </Link>
          <h2 className="mt-2 text-2xl font-semibold">{plant.name}</h2>
          <p className="mt-1 text-sm text-slate-600">
            Added {formatDate(plant.created_at)}
            {wasUpdated(plant.created_at, plant.updated_at) &&
              ` · Updated ${formatDate(plant.updated_at)}`}
          </p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <div className="flex items-center gap-2">
          {!isEditing && (
            <button
              type="button"
              onClick={() => setIsEditing(true)}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Edit
            </button>
          )}
          <button
            type="button"
            onClick={() => {
              if (window.confirm(`Delete ${plant.name}?`)) {
                deleteMutation.mutate();
              }
            }}
            disabled={deleteMutation.isPending}
            className="rounded-lg border border-red-200 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50 disabled:opacity-50"
          >
            Delete
          </button>
          </div>
          {deleteError && <p className="text-sm text-red-600">{deleteError}</p>}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Details</h3>
          {isEditing ? (
            <div className="mt-4">
              <PlantForm
                initialValues={{
                  name: plant.name,
                  species: plant.species ?? "",
                  location: plant.location ?? "",
                }}
                submitLabel="Save changes"
                onSubmit={async (values) => {
                  await updateMutation.mutateAsync(values);
                }}
                onCancel={() => setIsEditing(false)}
              />
            </div>
          ) : (
            <dl className="mt-4 space-y-3 text-sm">
              <div>
                <dt className="text-slate-500">Species</dt>
                <dd className="font-medium text-slate-900">{plant.species || "—"}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Location</dt>
                <dd className="font-medium text-slate-900">{plant.location || "—"}</dd>
              </div>
            </dl>
          )}
        </div>

        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-600">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Coming soon
          </h3>
          <ul className="mt-4 list-disc space-y-2 pl-5">
            <li>Notes and action log (Phase 2)</li>
            <li>Flush and refill schedule (Phase 3)</li>
            <li>Photos (Phase 4)</li>
          </ul>
        </div>
      </div>
    </section>
  );
}
