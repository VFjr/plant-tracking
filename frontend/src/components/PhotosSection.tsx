import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import { deletePhoto, fetchPhotos, photoFileUrl, uploadPhoto } from "../api/photos";
import { formatDate } from "../lib/dates";

type PhotosSectionProps = {
  plantId: number;
};

export function PhotosSection({ plantId }: PhotosSectionProps) {
  const queryClient = useQueryClient();
  const [caption, setCaption] = useState("");
  const [takenAt, setTakenAt] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [lightboxPhotoId, setLightboxPhotoId] = useState<number | null>(null);

  const { data: photos, isLoading, isError } = useQuery({
    queryKey: ["plants", plantId, "photos"],
    queryFn: () => fetchPhotos(plantId),
  });

  const uploadMutation = useMutation({
    mutationFn: ({ file, caption: note, taken_at }: { file: File; caption: string; taken_at: string }) =>
      uploadPhoto(plantId, file, {
        caption: note || undefined,
        taken_at: taken_at || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plants", plantId, "photos"] });
      setCaption("");
      setError(null);
    },
    onError: () => setError("Failed to upload photo."),
  });

  const deleteMutation = useMutation({
    mutationFn: deletePhoto,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plants", plantId, "photos"] });
      setLightboxPhotoId(null);
    },
  });

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const fileInput = form.elements.namedItem("photo-file") as HTMLInputElement;
    const file = fileInput.files?.[0];
    if (!file) {
      setError("Choose a photo to upload.");
      return;
    }
    await uploadMutation.mutateAsync({ file, caption, taken_at: takenAt });
    fileInput.value = "";
  }

  const lightboxPhoto = photos?.find((photo) => photo.id === lightboxPhotoId) ?? null;

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Photos</h3>

      <form onSubmit={handleSubmit} className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="sm:col-span-2">
          <label htmlFor="photo-file" className="mb-1 block text-sm font-medium text-slate-700">
            Image
          </label>
          <input
            id="photo-file"
            name="photo-file"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="w-full text-sm text-slate-700 file:mr-3 file:rounded-lg file:border-0 file:bg-emerald-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-emerald-800 hover:file:bg-emerald-100"
            required
          />
        </div>
        <div>
          <label htmlFor="photo-caption" className="mb-1 block text-sm font-medium text-slate-700">
            Caption (optional)
          </label>
          <input
            id="photo-caption"
            type="text"
            value={caption}
            onChange={(event) => setCaption(event.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
          />
        </div>
        <div>
          <label htmlFor="photo-taken-at" className="mb-1 block text-sm font-medium text-slate-700">
            Taken on (optional)
          </label>
          <input
            id="photo-taken-at"
            type="date"
            value={takenAt}
            onChange={(event) => setTakenAt(event.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
          />
        </div>
        {error && <p className="text-sm text-red-600 sm:col-span-2">{error}</p>}
        <div className="sm:col-span-2">
          <button
            type="submit"
            disabled={uploadMutation.isPending}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
          >
            {uploadMutation.isPending ? "Uploading..." : "Upload photo"}
          </button>
        </div>
      </form>

      <div className="mt-6">
        {isLoading && <p className="text-sm text-slate-600">Loading photos...</p>}
        {isError && <p className="text-sm text-red-600">Failed to load photos.</p>}
        {!isLoading && !isError && photos?.length === 0 && (
          <p className="text-sm text-slate-600">No photos yet.</p>
        )}
        {!isLoading && !isError && photos && photos.length > 0 && (
          <ul className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
            {photos.map((photo) => (
              <li key={photo.id} className="group relative overflow-hidden rounded-lg border border-slate-200">
                <button
                  type="button"
                  onClick={() => setLightboxPhotoId(photo.id)}
                  className="block w-full"
                >
                  <img
                    src={photoFileUrl(photo.id)}
                    alt={photo.caption ?? photo.filename}
                    className="aspect-square w-full object-cover"
                    loading="lazy"
                  />
                </button>
                <div className="space-y-1 p-2 text-xs">
                  {photo.caption && <p className="font-medium text-slate-900">{photo.caption}</p>}
                  <p className="text-slate-500">
                    {photo.taken_at ? `Taken ${formatDate(photo.taken_at)}` : formatDate(photo.uploaded_at)}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    if (window.confirm("Delete this photo?")) {
                      deleteMutation.mutate(photo.id);
                    }
                  }}
                  className="absolute right-2 top-2 rounded bg-white/90 px-2 py-1 text-xs font-medium text-red-700 opacity-0 shadow-sm transition group-hover:opacity-100 hover:bg-white"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {lightboxPhoto && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
          onClick={() => setLightboxPhotoId(null)}
          onKeyDown={(event) => {
            if (event.key === "Escape") {
              setLightboxPhotoId(null);
            }
          }}
          role="presentation"
        >
          <div
            className="max-h-full max-w-4xl"
            onClick={(event) => event.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-label="Photo preview"
          >
            <img
              src={photoFileUrl(lightboxPhoto.id)}
              alt={lightboxPhoto.caption ?? lightboxPhoto.filename}
              className="max-h-[80vh] w-full object-contain"
            />
            {(lightboxPhoto.caption || lightboxPhoto.taken_at) && (
              <div className="mt-2 text-center text-sm text-white">
                {lightboxPhoto.caption}
                {lightboxPhoto.caption && lightboxPhoto.taken_at && " · "}
                {lightboxPhoto.taken_at && `Taken ${formatDate(lightboxPhoto.taken_at)}`}
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
