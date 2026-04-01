import { LoaderCircleIcon } from "lucide-react";
import { type FormEvent, useEffect, useId, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { RegionCard, RouteCard, StationCard } from "@/components/cards";
import { InstanceSkeletonGrid } from "@/components/cards/InstanceSkeletonGrid";
import { PaginationControls } from "@/components/PaginationControls";
import { BentoGrid } from "@/components/ui/bento-grid";
import type { SearchResultItem } from "@/lib/api";
import { useSearchQuery } from "@/lib/queries";
import type { Pagination } from "@/types/api";

const DEFAULT_PAGE_SIZE = 24;
const PAGE_SIZE_OPTIONS = [12, 24, 48, 96] as const;

function parsePositiveInt(value: string | null, fallback: number): number {
  const parsed = Number.parseInt(value ?? "", 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function normalizePageSize(value: number): number {
  return PAGE_SIZE_OPTIONS.includes(value as (typeof PAGE_SIZE_OPTIONS)[number])
    ? value
    : DEFAULT_PAGE_SIZE;
}

function SearchResultCard({
  result,
  highlightQuery,
}: {
  result: SearchResultItem;
  highlightQuery?: string;
}) {
  if (result.modelType === "region") {
    return <RegionCard region={result.item} highlightQuery={highlightQuery} />;
  }
  if (result.modelType === "station") {
    return (
      <StationCard station={result.item} highlightQuery={highlightQuery} />
    );
  }
  return <RouteCard route={result.item} highlightQuery={highlightQuery} />;
}

function SearchLoadingState() {
  return (
    <div className="space-y-4" aria-live="polite">
      <div className="flex items-center gap-2 text-muted-foreground">
        <LoaderCircleIcon className="size-5 animate-spin" />
        <span className="font-medium text-sm">Searching...</span>
      </div>
      <InstanceSkeletonGrid count={20} />
    </div>
  );
}

function SearchContent({
  query,
  page,
  pageSize,
  onPageChange,
  onPageSizeChange,
}: {
  query: string;
  page: number;
  pageSize: number;
  onPageChange: (nextPage: number) => void;
  onPageSizeChange: (nextPageSize: number) => void;
}) {
  const searchQuery = useSearchQuery({ q: query, full: 1 });
  const allResults = searchQuery.data?.data ?? [];

  if (!query.trim()) {
    return (
      <p className="mb-8 text-muted-foreground">
        Enter a search query to find stations, routes, and regions.
      </p>
    );
  }

  if (searchQuery.isPending) {
    return <SearchLoadingState />;
  }

  const totalItems = allResults.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const currentPage = Math.min(Math.max(1, page), totalPages);
  const start = (currentPage - 1) * pageSize;
  const results = allResults.slice(start, start + pageSize);
  const links = searchQuery.data?.pagination.links ?? {
    self: "",
    next: null,
    previous: null,
    first: "",
    last: "",
  };
  const pagination: Pagination = {
    totalItems,
    totalPages,
    currentPage,
    pageSize,
    hasNextPage: currentPage < totalPages,
    hasPreviousPage: currentPage > 1,
    links,
  };

  return (
    <>
      <p className="mb-8 text-muted-foreground">
        Showing {results.length} of {pagination.totalItems} results for "{query}
        "
      </p>
      {searchQuery.isFetching ? (
        <div
          className="mb-4 flex items-center gap-2 text-muted-foreground"
          aria-live="polite"
        >
          <LoaderCircleIcon className="size-4 animate-spin" />
          <span className="font-medium text-sm">Searching...</span>
        </div>
      ) : null}
      <PaginationControls
        pagination={pagination}
        onPageChange={onPageChange}
        onPageSizeChange={onPageSizeChange}
      />
      {results.length === 0 ? (
        <p className="text-muted-foreground">No matching results found.</p>
      ) : (
        <BentoGrid className="lg:grid-rows-1">
          {results.map((result, index) => {
            const name = String(result.item.name ?? "result");
            return (
              <SearchResultCard
                key={`${result.modelType}-${name}-${index}`}
                result={result}
                highlightQuery={query}
              />
            );
          })}
        </BentoGrid>
      )}
    </>
  );
}

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const searchInputId = useId();

  const query = searchParams.get("q") || "";
  const page = parsePositiveInt(searchParams.get("page"), 1);
  const pageSize = normalizePageSize(
    parsePositiveInt(searchParams.get("pageSize"), DEFAULT_PAGE_SIZE),
  );

  const [inputValue, setInputValue] = useState(query);

  useEffect(() => {
    setInputValue(query);
  }, [query]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const next = new URLSearchParams(searchParams);
    const trimmed = inputValue.trim();
    if (trimmed) {
      next.set("q", trimmed);
    } else {
      next.delete("q");
    }
    next.set("page", "1");
    setSearchParams(next, { replace: true });
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-8 font-bold text-3xl tracking-tight">Search</h1>

      <form
        onSubmit={handleSubmit}
        className="mb-8 flex flex-wrap items-end gap-4"
      >
        <div className="min-w-72 grow">
          <label
            htmlFor={searchInputId}
            className="mb-1 block font-medium text-sm"
          >
            Search Entire Site
          </label>
          <input
            id={searchInputId}
            className="w-full rounded border bg-background p-2"
            value={inputValue}
            onChange={(event) => setInputValue(event.target.value)}
            placeholder="Try: texas eagle"
          />
        </div>
        <button
          type="submit"
          className="h-10 rounded border bg-background px-4 font-medium text-sm"
        >
          Search
        </button>
      </form>

      <SearchContent
        query={query}
        page={page}
        pageSize={pageSize}
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
    </div>
  );
}
