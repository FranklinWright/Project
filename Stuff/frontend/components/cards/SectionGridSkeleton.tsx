import { useMemo } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { BentoCardSkeleton } from "./BentoCardSkeleton";

interface SectionGridSkeletonProps {
  showTitle?: boolean;
  cardCount?: number;
}

export function SectionGridSkeleton({
  showTitle = true,
  cardCount = 3,
}: SectionGridSkeletonProps) {
  const keys = useMemo(
    () => Array.from({ length: cardCount }, () => crypto.randomUUID()),
    [cardCount],
  );
  return (
    <div className="mt-12">
      {showTitle && <Skeleton className="mb-6 h-8 w-48" />}
      <div
        className="grid w-full grid-cols-3 gap-4"
        style={{ gridAutoRows: "minmax(22rem, auto)" }}
      >
        {keys.map((key) => (
          <BentoCardSkeleton key={key} />
        ))}
      </div>
    </div>
  );
}
