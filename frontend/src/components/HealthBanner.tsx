import { useQuery } from "@tanstack/react-query";
import { fetchHealth } from "../api/client";

export function HealthBanner() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    retry: 1,
  });

  if (isLoading) {
    return (
      <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-600">
        Checking API connection...
      </div>
    );
  }

  if (isError || data?.status !== "ok") {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
        API unreachable. Start the backend with <code className="font-mono">make dev-api</code>.
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm text-emerald-700">
      API connected
    </div>
  );
}
