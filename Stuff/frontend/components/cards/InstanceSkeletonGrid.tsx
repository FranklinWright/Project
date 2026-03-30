import { Skeleton } from "@/components/ui/skeleton";

export function InstanceSkeletonGrid({ count = 20 }: { count?: number }) {
  return (
    <>
      <Skeleton className="mb-8 h-5 w-48" />
      <div
        className="grid w-full grid-cols-3 gap-4"
        style={{ gridAutoRows: "minmax(22rem, auto)" }}
      >
        {Array.from({ length: count }, (_, i) => i).map((i) => (
          <Skeleton
            key={i}
            className="col-span-3 min-h-88 rounded-xl lg:col-span-1"
          />
        ))}
      </div>
    </>
  );
}
