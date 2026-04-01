import type {
  Pagination,
  Region,
  RegionsListResponse,
  Route,
  RoutesListResponse,
  Station,
  StationsListResponse,
} from "@/types/api";

const API_BASE =
  typeof window === "undefined"
    ? `${process.env.API_BASE ?? "http://localhost:3001"}/api`
    : "/api";

export interface ListQueryParams {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  direction?: "asc" | "desc";
  [key: string]: string | number | undefined;
}

export interface SearchQueryParams {
  q?: string;
  page?: number;
  pageSize?: number;
  full?: number;
}

export type SearchResultItem =
  | { modelType: "region"; score: number; item: Region }
  | { modelType: "station"; score: number; item: Station }
  | { modelType: "route"; score: number; item: Route };

export interface SearchResponse {
  data: SearchResultItem[];
  pagination: Pagination;
  query: string;
}

const SEARCH_BATCH_SIZE = 100;

function buildPaginatedUrl(path: string, params: ListQueryParams = {}): string {
  const searchParams = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  }

  const queryString = searchParams.toString();
  return queryString
    ? `${API_BASE}${path}?${queryString}`
    : `${API_BASE}${path}`;
}

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error ?? "Request failed");
  }
  return res.json();
}

export function fetchRegions(
  params: ListQueryParams = {},
): Promise<RegionsListResponse> {
  return fetchJson(buildPaginatedUrl("/regions", params));
}

export function fetchRegion(idOrCode: string): Promise<Region> {
  return fetchJson(`${API_BASE}/regions/${encodeURIComponent(idOrCode)}`);
}

export function fetchStations(
  params: ListQueryParams = {},
): Promise<StationsListResponse> {
  return fetchJson(buildPaginatedUrl("/stations", params));
}

export function fetchStation(idOrCode: string): Promise<Station> {
  return fetchJson(`${API_BASE}/stations/${encodeURIComponent(idOrCode)}`);
}

export function fetchRoutes(
  params: ListQueryParams = {},
): Promise<RoutesListResponse> {
  return fetchJson(buildPaginatedUrl("/routes", params));
}

export function fetchRoute(idOrSlug: string): Promise<Route> {
  return fetchJson(`${API_BASE}/routes/${encodeURIComponent(idOrSlug)}`);
}

export function fetchSearch(
  params: SearchQueryParams = {},
): Promise<SearchResponse> {
  return fetchJson(buildPaginatedUrl("/search", params as ListQueryParams));
}

export async function fetchSearchAll(
  params: SearchQueryParams = {},
): Promise<SearchResponse> {
  const query = (params.q ?? "").trim();
  const first = await fetchSearch({
    q: query,
    page: 1,
    pageSize: SEARCH_BATCH_SIZE,
    full: params.full ?? 1,
  });

  const expectedTotal = Math.max(
    first.pagination.totalItems,
    first.data.length,
  );
  if (first.data.length >= expectedTotal) {
    return first;
  }

  const merged: SearchResultItem[] = [...first.data];
  const seen = new Set<string>(
    merged.map((entry) => `${entry.modelType}:${entry.item.id}`),
  );

  const totalPages = Math.max(first.pagination.totalPages, 1);
  for (let nextPage = 2; nextPage <= totalPages; nextPage += 1) {
    const next = await fetchSearch({
      q: query,
      page: nextPage,
      pageSize: SEARCH_BATCH_SIZE,
    });
    for (const entry of next.data) {
      const key = `${entry.modelType}:${entry.item.id}`;
      if (seen.has(key)) {
        continue;
      }
      seen.add(key);
      merged.push(entry);
    }
    if (merged.length >= expectedTotal) {
      break;
    }
  }

  return {
    ...first,
    data: merged,
    pagination: {
      ...first.pagination,
      totalItems: merged.length,
      totalPages: 1,
      currentPage: 1,
      pageSize: Math.max(1, merged.length),
      hasNextPage: false,
      hasPreviousPage: false,
    },
  };
}
