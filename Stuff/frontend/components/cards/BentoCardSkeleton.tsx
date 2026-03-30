import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface BentoCardSkeletonProps {
  className?: string;
}

export function BentoCardSkeleton({ className }: BentoCardSkeletonProps) {
  return (
    <div
      className={cn(
        "col-span-3 flex flex-col overflow-hidden rounded-xl border bg-background p-4 lg:col-span-1",
        className,
      )}
    >
      <Skeleton className="mb-2 h-8 w-8" />
      <Skeleton className="mb-2 h-6 w-32" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="mt-2 h-4 w-3/4" />
      <Skeleton className="mt-1 h-4 w-1/2" />
    </div>
  );
}
