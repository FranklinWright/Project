import type { ReactNode } from "react";
import { BentoGrid } from "@/components/ui/bento-grid";

interface SectionWithGridProps {
  title: string;
  children: ReactNode;
  gridClassName?: string;
}

export function SectionWithGrid({
  title,
  children,
  gridClassName,
}: SectionWithGridProps) {
  return (
    <div className="mt-12">
      <h2 className="mb-6 font-bold text-2xl">{title}</h2>
      <BentoGrid className={gridClassName}>{children}</BentoGrid>
    </div>
  );
}
