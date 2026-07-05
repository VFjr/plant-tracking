import { type FormEvent, useState } from "react";
import type { PlantCreate } from "../api/plants";

type PlantFormValues = {
  name: string;
  species: string;
  location: string;
};

type PlantFormProps = {
  initialValues?: Partial<PlantFormValues>;
  submitLabel: string;
  onSubmit: (values: PlantCreate) => Promise<void>;
  onCancel?: () => void;
};

export function PlantForm({
  initialValues,
  submitLabel,
  onSubmit,
  onCancel,
}: PlantFormProps) {
  const [name, setName] = useState(initialValues?.name ?? "");
  const [species, setSpecies] = useState(initialValues?.species ?? "");
  const [location, setLocation] = useState(initialValues?.location ?? "");
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
      await onSubmit({
        name: name.trim(),
        species: species.trim() || null,
        location: location.trim() || null,
      });
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
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
