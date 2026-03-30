import type {
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
}

function buildPaginatedUrl(path: string, params: ListQueryParams = {}): string {
  const searchParams = new URLSearchParams();

  if (typeof params.page === "number") {
    searchParams.set("page", String(params.page));
  }

  if (typeof params.pageSize === "number") {
    searchParams.set("pageSize", String(params.pageSize));
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
