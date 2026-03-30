import { Suspense } from "react";
import { useSearchParams } from "react-router-dom";
import { StationCard } from "@/components/cards";
import { InstanceSkeletonGrid } from "@/components/cards/InstanceSkeletonGrid";
import { PaginationControls } from "@/components/PaginationControls";
import { BentoGrid } from "@/components/ui/bento-grid";
import { useStationsQuery } from "@/lib/queries";

const DEFAULT_PAGE_SIZE = 24;

function parsePositiveInt(value: string | null, fallback: number): number {
  const parsed = Number.parseInt(value ?? "", 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function StationsContent({
  page,
  pageSize,
  onPageChange,
  onPageSizeChange,
}: {
  page: number;
  pageSize: number;
  onPageChange: (nextPage: number) => void;
  onPageSizeChange: (nextPageSize: number) => void;
}) {
  const {
    data: { data: stations = [], pagination },
  } = useStationsQuery({ page, pageSize });

  return (
    <>
      <p className="mb-8 text-muted-foreground">
        Showing {stations.length} of {pagination.totalItems} instances
      </p>
      <PaginationControls
        pagination={pagination}
        onPageChange={onPageChange}
        onPageSizeChange={onPageSizeChange}
      />
      <BentoGrid className="lg:grid-rows-1">
        {stations.map((station) => (
          <StationCard key={station.code} station={station} />
        ))}
      </BentoGrid>
    </>
  );
}

export function StationsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = parsePositiveInt(searchParams.get("page"), 1);
  const pageSize = parsePositiveInt(
    searchParams.get("pageSize"),
    DEFAULT_PAGE_SIZE,
  );

  function setPagination(nextPage: number, nextPageSize: number) {
    const nextParams = new URLSearchParams(searchParams);
    nextParams.set("page", String(Math.max(1, nextPage)));
    nextParams.set("pageSize", String(Math.max(1, nextPageSize)));
    setSearchParams(nextParams, { replace: true });
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-8 font-bold text-3xl tracking-tight">Stations</h1>
      <Suspense fallback={<InstanceSkeletonGrid />}>
        <StationsContent
          page={page}
          pageSize={pageSize}
          onPageChange={(nextPage) => setPagination(nextPage, pageSize)}
          onPageSizeChange={(nextPageSize) => setPagination(1, nextPageSize)}
        />
      </Suspense>
    </div>
  );
}
