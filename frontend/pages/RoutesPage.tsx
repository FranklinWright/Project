import { Suspense, useId } from "react";
import { useSearchParams } from "react-router-dom";
import { RouteCard } from "@/components/cards";
import { InstanceSkeletonGrid } from "@/components/cards/InstanceSkeletonGrid";
import { PaginationControls } from "@/components/PaginationControls";
import { BentoGrid } from "@/components/ui/bento-grid";
import { useRoutesQuery } from "@/lib/queries";

const DEFAULT_PAGE_SIZE = 24;

function parsePositiveInt(value: string | null, fallback: number): number {
  const parsed = Number.parseInt(value ?? "", 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function RoutesContent({
  page,
  pageSize,
  filters,
  onPageChange,
  onPageSizeChange,
}: {
  page: number;
  pageSize: number;
  filters: { q?: string };
  onPageChange: (nextPage: number) => void;
  onPageSizeChange: (nextPageSize: number) => void;
}) {
  const {
    data: { data: routes = [], pagination },
  } = useRoutesQuery({
    page,
    pageSize,
    ...filters,
  });

  return (
    <>
      <p className="mb-8 text-muted-foreground">
        Showing {routes.length} of {pagination.totalItems} instances
      </p>
      <PaginationControls
        pagination={pagination}
        onPageChange={onPageChange}
        onPageSizeChange={onPageSizeChange}
      />
      <BentoGrid className="lg:grid-rows-1">
        {routes.map((route) => (
          <RouteCard
            key={route.name}
            route={route}
            highlightQuery={filters.q}
          />
        ))}
      </BentoGrid>
    </>
  );
}

export function RoutesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const searchId = useId();

  const page = parsePositiveInt(searchParams.get("page"), 1);
  const pageSize = parsePositiveInt(
    searchParams.get("pageSize"),
    DEFAULT_PAGE_SIZE,
  );

  const filters = {
    q: searchParams.get("q") || "",
  };

  function setParam(key: string, value: string) {
    const nextParams = new URLSearchParams(searchParams);
    if (value) nextParams.set(key, value);
    else nextParams.delete(key);
    nextParams.set("page", "1");
    setSearchParams(nextParams, { replace: true });
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-8 font-bold text-3xl tracking-tight">Routes</h1>

      <div className="mb-8">
        <label htmlFor={searchId} className="mb-1 block font-medium text-sm">
          Search
        </label>
        <input
          id={searchId}
          className="rounded border bg-background p-2"
          value={filters.q}
          onChange={(e) => setParam("q", e.target.value)}
          placeholder="Search routes..."
        />
      </div>

      <Suspense fallback={<InstanceSkeletonGrid />}>
        <RoutesContent
          page={page}
          pageSize={pageSize}
          filters={filters}
          onPageChange={(nextPage) => {
            const next = new URLSearchParams(searchParams);
            next.set("page", String(nextPage));
            setSearchParams(next);
          }}
          onPageSizeChange={(nextPageSize) => {
            const next = new URLSearchParams(searchParams);
            next.set("pageSize", String(nextPageSize));
            next.set("page", "1");
            setSearchParams(next);
          }}
        />
      </Suspense>
    </div>
  );
}
