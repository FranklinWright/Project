import { Suspense, useId } from "react";
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
  sortBy,
  direction,
  filters,
  onPageChange,
  onPageSizeChange,
}: {
  page: number;
  pageSize: number;
  sortBy: string;
  direction: "asc" | "desc";
  filters: {
    q?: string;
    timezone?: string;
    ada_accessible?: string;
  };
  onPageChange: (nextPage: number) => void;
  onPageSizeChange: (nextPageSize: number) => void;
}) {
  const showZero = filters.ada_accessible === "No";

  const {
    data: { data: stations = [], pagination },
  } = useStationsQuery({
    page,
    pageSize,
    sortBy,
    direction,
    ...filters,
  });

  if (showZero || stations.length === 0) {
    return (
      <>
        <p className="mb-8 text-muted-foreground italic">
          Showing 0 of 0 instances
        </p>
        <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed py-20 opacity-50">
          <p className="text-center font-medium text-muted-foreground text-xl">
            {showZero
              ? "No non-accessible stations found."
              : "No matching stations found."}
          </p>
        </div>
      </>
    );
  }

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
          <StationCard
            key={station.code}
            station={station}
            highlightQuery={filters.q}
          />
        ))}
      </BentoGrid>
    </>
  );
}

export function StationsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const searchId = useId();
  const timezoneId = useId();
  const adaId = useId();
  const sortId = useId();
  const orderId = useId();

  const page = parsePositiveInt(searchParams.get("page"), 1);
  const pageSize = parsePositiveInt(
    searchParams.get("pageSize"),
    DEFAULT_PAGE_SIZE,
  );
  const sortBy = searchParams.get("sortBy") || "name";
  const direction = (searchParams.get("direction") as "asc" | "desc") || "asc";

  const filters = {
    q: searchParams.get("q") || "",
    timezone: searchParams.get("timezone") || "",
    ada_accessible: searchParams.get("ada_accessible") || "",
  };

  function setParam(key: string, value: string) {
    const nextParams = new URLSearchParams(searchParams);
    if (value && value !== "all") nextParams.set(key, value);
    else nextParams.delete(key);
    nextParams.set("page", "1");
    setSearchParams(nextParams, { replace: true });
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-8 font-bold text-3xl tracking-tight">Stations</h1>

      <div className="mb-8 flex flex-wrap items-end gap-4">
        <div>
          <label htmlFor={searchId} className="mb-1 block font-medium text-sm">
            Search
          </label>
          <input
            id={searchId}
            className="rounded border bg-background p-2"
            value={filters.q}
            onChange={(e) => setParam("q", e.target.value)}
            placeholder="Search stations..."
          />
        </div>

        <div>
          <label
            htmlFor={timezoneId}
            className="mb-1 block font-medium text-sm"
          >
            Timezone
          </label>
          <select
            id={timezoneId}
            className="rounded border bg-background p-2"
            value={filters.timezone || "all"}
            onChange={(e) => setParam("timezone", e.target.value)}
          >
            <option value="all">All Timezones</option>
            <option value="America/New_York">Eastern</option>
            <option value="America/Chicago">Central</option>
            <option value="America/Denver">Mountain</option>
            <option value="America/Los_Angeles">Pacific</option>
          </select>
        </div>

        <div>
          <label htmlFor={adaId} className="mb-1 block font-medium text-sm">
            ADA Accessible
          </label>
          <select
            id={adaId}
            className="rounded border bg-background p-2"
            value={filters.ada_accessible || "all"}
            onChange={(e) => setParam("ada_accessible", e.target.value)}
          >
            <option value="all">All Stations</option>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
        </div>

        <div>
          <label htmlFor={sortId} className="mb-1 block font-medium text-sm">
            Sort By
          </label>
          <select
            id={sortId}
            className="rounded border bg-background p-2"
            value={sortBy}
            onChange={(e) => setParam("sortBy", e.target.value)}
          >
            <option value="name">Name</option>
            <option value="routes_served_count">Routes Served</option>
            <option value="hours">Opening Time</option>
          </select>
        </div>

        <div>
          <label htmlFor={orderId} className="mb-1 block font-medium text-sm">
            Order
          </label>
          <select
            id={orderId}
            className="rounded border bg-background p-2"
            value={direction}
            onChange={(e) => setParam("direction", e.target.value)}
          >
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
          </select>
        </div>
      </div>

      <Suspense fallback={<InstanceSkeletonGrid />}>
        <StationsContent
          page={page}
          pageSize={pageSize}
          sortBy={sortBy}
          direction={direction}
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
