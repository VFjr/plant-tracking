import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL ?? "";

export const api = axios.create({ baseURL });

export type HealthResponse = {
  status: string;
};

export async function fetchHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>("/api/health");
  return data;
}
