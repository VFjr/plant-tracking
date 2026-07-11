import { api } from "./client";

export type DashboardTask = {
  plant_id: number;
  plant_name: string;
  task: "flush";
  due_date: string;
  has_flush_interval: boolean;
  has_been_flushed: boolean;
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
