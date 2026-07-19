import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { createPlant } from "../api/plants";
import { PlantForm } from "../components/PlantForm";

export function PlantNewPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createPlant,
    onSuccess: (plant) => {
      queryClient.invalidateQueries({ queryKey: ["plants"] });
      navigate(`/plants/${plant.id}`);
    },
  });

  return (
    <section className="mx-auto max-w-xl space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Add plant or cutting</h2>
        <p className="mt-1 text-sm text-slate-600">
          Create a new semi-hydro plant or water cutting entry.
        </p>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <PlantForm
          showKindSelector
          submitLabel="Create entry"
          onSubmit={async (values) => {
            await mutation.mutateAsync(values);
          }}
          onCancel={() => navigate("/plants")}
        />
      </div>
    </section>
  );
}
