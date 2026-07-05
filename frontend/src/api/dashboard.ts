import { api } from "./client";

export type DashboardTask = {
  plant_id: number;
  plant_name: string;
  task: "flush";
  due_date: string;
};

export type Dashboard = {
  overdue: DashboardTask[];
  due_today: DashboardTask[];
};

export async function fetchDashboard(): Promise<Dashboard> {
  const { data } = await api.get<Dashboard>("/api/dashboard");
  return data;
}
