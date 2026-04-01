import { Fragment, type ReactNode } from "react";

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export function highlightText(
  value: string | number | null | undefined,
  query?: string,
): ReactNode {
  if (value === null || value === undefined) {
    return "";
  }

  const text = String(value);
  const normalizedQuery = (query ?? "").trim();

  if (!text || !normalizedQuery) {
    return text;
  }

  const pattern = new RegExp(`(${escapeRegExp(normalizedQuery)})`, "gi");
  const parts = text.split(pattern);
  const queryLower = normalizedQuery.toLowerCase();
  let cursor = 0;

  return parts.map((part) => {
    const key = `${cursor}-${part.length}`;
    cursor += part.length;

    if (part.toLowerCase() === queryLower) {
      return (
        <mark
          key={`m-${key}`}
          className="rounded bg-amber-200/95 px-1 text-black"
        >
          {part}
        </mark>
      );
    }

    return <Fragment key={`t-${key}`}>{part}</Fragment>;
  });
}
