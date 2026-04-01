import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** True if value is defined and has content (non-empty string, any number including 0). */
export function hasValue(
  v: string | number | null | undefined,
): v is string | number {
  if (v === null || v === undefined) return false;
  if (typeof v === "string") return v.trim() !== "";
  return true;
}

/** True if array exists and has at least one item. */
export function hasItems<T>(arr: T[] | null | undefined): arr is T[] {
  return Array.isArray(arr) && arr.length > 0;
}
