import { NavLink, Outlet } from "react-router-dom";
import { HealthBanner } from "./HealthBanner";

const linkClass = ({ isActive }: { isActive: boolean }) =>
  isActive
    ? "rounded-md bg-emerald-100 px-3 py-2 text-sm font-medium text-emerald-800"
    : "rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900";

export function Layout() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-emerald-700">
              Semi-Hydro
            </p>
            <h1 className="text-xl font-semibold">Plant Tracker</h1>
          </div>
          <nav className="flex items-center gap-2">
            <NavLink to="/" className={linkClass} end>
              Dashboard
            </NavLink>
            <NavLink to="/plants" className={linkClass}>
              Plants
            </NavLink>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-6">
        <div className="mb-6">
          <HealthBanner />
        </div>
        <Outlet />
      </main>
    </div>
  );
}
