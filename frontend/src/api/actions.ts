import { api } from "./client";

export type ActionType = "flush" | "reservoir_refill" | "other";

export type ActionEntry = {
  id: number;
  plant_id: number;
  action_type: ActionType;
  performed_at: string;
  notes: string | null;
  created_at: string;
};

export type ActionCreate = {
  action_type: ActionType;
  performed_at: string;
  notes?: string | null;
};

export const ACTION_TYPE_LABELS: Record<ActionType, string> = {
  flush: "Flush",
  reservoir_refill: "Reservoir refill",
  other: "Other",
};

export async function fetchActions(plantId: number): Promise<ActionEntry[]> {
  const { data } = await api.get<ActionEntry[]>(`/api/plants/${plantId}/actions`);
  return data;
}

export async function createAction(plantId: number, action: ActionCreate): Promise<ActionEntry> {
  const { data } = await api.post<ActionEntry>(`/api/plants/${plantId}/actions`, action);
  return data;
}

export async function deleteAction(actionId: number): Promise<void> {
  await api.delete(`/api/actions/${actionId}`);
}
