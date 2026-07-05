import { api } from "./client";

export type Plant = {
  id: number;
  name: string;
  species: string | null;
  location: string | null;
  description: string | null;
  flush_interval_days: number | null;
  next_flush_date: string | null;
  last_flush_date: string | null;
  created_at: string;
  updated_at: string;
};

export type PlantCreate = {
  name: string;
  species?: string | null;
  location?: string | null;
  description?: string | null;
};

export type PlantUpdate = {
  name?: string;
  species?: string | null;
  location?: string | null;
  description?: string | null;
};

export type PlantScheduleUpdate = {
  flush_interval_days?: number | null;
};

export async function fetchPlants(): Promise<Plant[]> {
  const { data } = await api.get<Plant[]>("/api/plants");
  return data;
}

export async function fetchPlant(id: number): Promise<Plant> {
  const { data } = await api.get<Plant>(`/api/plants/${id}`);
  return data;
}

export async function createPlant(plant: PlantCreate): Promise<Plant> {
  const { data } = await api.post<Plant>("/api/plants", plant);
  return data;
}

export async function updatePlant(id: number, plant: PlantUpdate): Promise<Plant> {
  const { data } = await api.patch<Plant>(`/api/plants/${id}`, plant);
  return data;
}

export async function updatePlantSchedule(
  id: number,
  schedule: PlantScheduleUpdate,
): Promise<Plant> {
  const { data } = await api.patch<Plant>(`/api/plants/${id}/schedule`, schedule);
  return data;
}

export async function deletePlant(id: number): Promise<void> {
  await api.delete(`/api/plants/${id}`);
}
