import { api } from "./client";

export type Note = {
  id: number;
  plant_id: number;
  content: string;
  created_at: string;
};

export type NoteCreate = {
  content: string;
};

export async function fetchNotes(plantId: number): Promise<Note[]> {
  const { data } = await api.get<Note[]>(`/api/plants/${plantId}/notes`);
  return data;
}

export async function createNote(plantId: number, note: NoteCreate): Promise<Note> {
  const { data } = await api.post<Note>(`/api/plants/${plantId}/notes`, note);
  return data;
}

export async function deleteNote(noteId: number): Promise<void> {
  await api.delete(`/api/notes/${noteId}`);
}
