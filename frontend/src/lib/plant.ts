export function wasUpdated(createdAt: string, updatedAt: string): boolean {
  return new Date(updatedAt).getTime() !== new Date(createdAt).getTime();
}
