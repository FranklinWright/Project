import { Skeleton } from "@/components/ui/skeleton";

export function PageHeaderSkeleton() {
  return (
    <div className="space-y-8">
      <Skeleton className="h-10 w-64" />
      <Skeleton className="aspect-video w-full rounded-xl" />
    </div>
  );
}
