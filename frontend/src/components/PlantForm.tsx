import { type FormEvent, useState } from "react";
import type { ManagedKind, PlantCreate } from "../api/plants";
import { KIND_LABELS } from "../api/plants";

type PlantFormValues = {
  name: string;
  kind: ManagedKind;
  species: string;
  location: string;
  description: string;
};

type PlantFormProps = {
  initialValues?: Partial<PlantFormValues>;
  submitLabel: string;
  showKindSelector?: boolean;
  onSubmit: (values: PlantCreate) => Promise<void>;
  onCancel?: () => void;
};

const DESCRIPTION_PLACEHOLDER: Record<ManagedKind, string> = {
  semi_hydro: "Setup, pot type, nutrient mix, general notes...",
  cutting: "Jar size, rooting hormone, water change notes...",
};

export function PlantForm({
  initialValues,
  submitLabel,
  showKindSelector = false,
  onSubmit,
  onCancel,
}: PlantFormProps) {
  const [name, setName] = useState(initialValues?.name ?? "");
  const [kind, setKind] = useState<ManagedKind>(initialValues?.kind ?? "semi_hydro");
  const [species, setSpecies] = useState(initialValues?.species ?? "");
  const [location, setLocation] = useState(initialValues?.location ?? "");
  const [description, setDescription] = useState(initialValues?.description ?? "");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!name.trim()) {
      setError("Name is required.");
      return;
    }

    setError(null);
    setIsSubmitting(true);
    try {
      const payload: PlantCreate = {
        name: name.trim(),
        species: species.trim() || null,
        location: location.trim() || null,
        description: description.trim() || null,
      };
      if (showKindSelector) {
        payload.kind = kind;
      }
      await onSubmit(payload);
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {showKindSelector && (
        <div>
          <label htmlFor="kind" className="mb-1 block text-sm font-medium text-slate-700">
            Type
          </label>
          <select
            id="kind"
            value={kind}
            onChange={(event) => setKind(event.target.value as ManagedKind)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
          >
            {(Object.keys(KIND_LABELS) as ManagedKind[]).map((option) => (
              <option key={option} value={option}>
                {KIND_LABELS[option]}
              </option>
            ))}
          </select>
        </div>
      )}

      <div>
        <label htmlFor="name" className="mb-1 block text-sm font-medium text-slate-700">
          Name
        </label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(event) => setName(event.target.value)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
          required
        />
      </div>

      <div>
        <label htmlFor="species" className="mb-1 block text-sm font-medium text-slate-700">
          Species
        </label>
        <input
          id="species"
          type="text"
          value={species}
          onChange={(event) => setSpecies(event.target.value)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
        />
      </div>

      <div>
        <label htmlFor="location" className="mb-1 block text-sm font-medium text-slate-700">
          Location
        </label>
        <input
          id="location"
          type="text"
          value={location}
          onChange={(event) => setLocation(event.target.value)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
        />
      </div>

      <div>
        <label htmlFor="description" className="mb-1 block text-sm font-medium text-slate-700">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          rows={4}
          placeholder={DESCRIPTION_PLACEHOLDER[showKindSelector ? kind : initialValues?.kind ?? "semi_hydro"]}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
        />
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
        >
          {isSubmitting ? "Saving..." : submitLabel}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
