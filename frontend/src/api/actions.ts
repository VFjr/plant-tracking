import { api } from "./client";
import type { ManagedKind } from "./plants";

export type ActionType =
  | "flush"
  | "reservoir_refill"
  | "monitor"
  | "water_change"
  | "other";

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
  monitor: "Monitor",
  water_change: "Water change",
  other: "Other",
};

export const ACTION_TYPES_BY_KIND: Record<ManagedKind, ActionType[]> = {
  semi_hydro: ["flush", "reservoir_refill", "other"],
  cutting: ["monitor", "water_change", "other"],
};

export const DEFAULT_ACTION_TYPE_BY_KIND: Record<ManagedKind, ActionType> = {
  semi_hydro: "flush",
  cutting: "monitor",
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
