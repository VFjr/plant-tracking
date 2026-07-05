import { api } from "./client";

export type Photo = {
  id: number;
  plant_id: number;
  filename: string;
  stored_name: string;
  caption: string | null;
  taken_at: string | null;
  uploaded_at: string;
};

export function photoFileUrl(photoId: number): string {
  return `/api/photos/${photoId}/file`;
}

export async function fetchPhotos(plantId: number): Promise<Photo[]> {
  const { data } = await api.get<Photo[]>(`/api/plants/${plantId}/photos`);
  return data;
}

export async function uploadPhoto(
  plantId: number,
  file: File,
  options?: { caption?: string; taken_at?: string },
): Promise<Photo> {
  const form = new FormData();
  form.append("file", file);
  if (options?.caption?.trim()) {
    form.append("caption", options.caption.trim());
  }
  if (options?.taken_at) {
    form.append("taken_at", options.taken_at);
  }
  const { data } = await api.post<Photo>(`/api/plants/${plantId}/photos`, form);
  return data;
}

export async function deletePhoto(photoId: number): Promise<void> {
  await api.delete(`/api/photos/${photoId}`);
}
