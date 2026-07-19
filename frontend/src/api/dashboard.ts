import { api } from "./client";

export type DashboardTask = {
  plant_id: number;
  plant_name: string;
  task: "flush" | "monitor";
  due_date: string;
  has_flush_interval?: boolean | null;
  has_been_flushed?: boolean | null;
  has_monitor_interval?: boolean | null;
  has_been_monitored?: boolean | null;
};

export type Dashboard = {
  overdue: DashboardTask[];
  due_today: DashboardTask[];
  needs_attention: DashboardTask[];
};

export async function fetchDashboard(): Promise<Dashboard> {
  const { data } = await api.get<Dashboard>("/api/dashboard");
  return data;
}
