import type { ReactNode } from "react";

export function CardFieldList({ children }: { children: ReactNode }) {
  return <div className="flex flex-col gap-1">{children}</div>;
}

export function CardField({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <p key={label}>
      <span className="font-semibold text-white">{label}</span>{" "}
      <span className="text-neutral-200">{children}</span>
    </p>
  );
}
