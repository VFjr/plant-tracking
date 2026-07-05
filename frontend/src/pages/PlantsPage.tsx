import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { fetchPlants } from "../api/plants";
import { FlushStatusBadge } from "../components/FlushStatusBadge";

export function PlantsPage() {
  const { data: plants, isLoading, isError } = useQuery({
    queryKey: ["plants"],
    queryFn: fetchPlants,
  });

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold">Plants</h2>
          <p className="mt-1 text-sm text-slate-600">Manage your semi-hydro plants.</p>
        </div>
        <Link
          to="/plants/new"
          className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
        >
          Add plant
        </Link>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
        {isLoading && <p className="p-6 text-sm text-slate-600">Loading plants...</p>}
        {isError && (
          <p className="p-6 text-sm text-red-600">Failed to load plants. Is the API running?</p>
        )}
        {!isLoading && !isError && plants?.length === 0 && (
          <p className="p-6 text-sm text-slate-600">
            No plants yet.{" "}
            <Link to="/plants/new" className="font-medium text-emerald-700 hover:underline">
              Add your first plant
            </Link>
            .
          </p>
        )}
        {!isLoading && !isError && plants && plants.length > 0 && (
          <ul className="divide-y divide-slate-200">
            {plants.map((plant) => (
              <li key={plant.id}>
                <Link
                  to={`/plants/${plant.id}`}
                  className="flex items-center justify-between gap-4 px-6 py-4 hover:bg-slate-50"
                >
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="font-medium text-slate-900">{plant.name}</p>
                      <FlushStatusBadge nextFlushDate={plant.next_flush_date} />
                    </div>
                    <p className="text-sm text-slate-600">
                      {[plant.species, plant.location].filter(Boolean).join(" · ") || "No details yet"}
                    </p>
                  </div>
                  <span className="text-sm text-emerald-700">View</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
