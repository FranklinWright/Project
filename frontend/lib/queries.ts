import { useQuery, useSuspenseQuery } from "@tanstack/react-query";
import {
  fetchRegion,
  fetchRegions,
  fetchRoute,
  fetchRoutes,
  fetchSearchAll,
  fetchStation,
  fetchStations,
  type ListQueryParams,
  type SearchQueryParams,
} from "./api";

const DEFAULT_PAGE = 1;
const DEFAULT_PAGE_SIZE = 24;

function normalizeListQueryParams(params: ListQueryParams = {}) {
  return {
    ...params,
    page: Math.max(1, params.page ?? DEFAULT_PAGE),
    pageSize: Math.max(1, params.pageSize ?? DEFAULT_PAGE_SIZE),
    sortBy: params.sortBy ?? "name",
    direction: params.direction ?? "asc",
  };
}

export const queryKeys = {
  regions: (params: ListQueryParams) => ["regions", params] as const,
  region: (idOrCode: string) => ["regions", idOrCode] as const,
  stations: (params: ListQueryParams) => ["stations", params] as const,
  station: (idOrCode: string) => ["stations", idOrCode] as const,
  routes: (params: ListQueryParams) => ["routes", params] as const,
  route: (idOrSlug: string) => ["routes", idOrSlug] as const,
  search: (params: SearchQueryParams) => ["search", params] as const,
  aboutMemberCommits: (gitlabUsername: string) =>
    ["about", "stats", "member", gitlabUsername, "commits"] as const,
  aboutMemberIssues: (gitlabUsername: string) =>
    ["about", "stats", "member", gitlabUsername, "issues"] as const,
};

function normalizeSearchQueryParams(params: SearchQueryParams = {}) {
  return {
    q: (params.q ?? "").trim(),
    full: params.full ?? 0,
  };
}

function regionsOptions(params: ListQueryParams = {}) {
  const normalized = normalizeListQueryParams(params);
  return {
    queryKey: queryKeys.regions(normalized),
    queryFn: async () => await fetchRegions(normalized),
  };
}

function regionOptions(id: string) {
  return {
    queryKey: queryKeys.region(id),
    queryFn: () => fetchRegion(id),
  };
}

function stationsOptions(params: ListQueryParams = {}) {
  const normalized = normalizeListQueryParams(params);
  return {
    queryKey: queryKeys.stations(normalized),
    queryFn: async () => await fetchStations(normalized),
  };
}

function stationOptions(id: string) {
  return {
    queryKey: queryKeys.station(id),
    queryFn: () => fetchStation(id),
  };
}

function routesOptions(params: ListQueryParams = {}) {
  const normalized = normalizeListQueryParams(params);
  return {
    queryKey: queryKeys.routes(normalized),
    queryFn: async () => await fetchRoutes(normalized),
  };
}

function routeOptions(id: string) {
  return {
    queryKey: queryKeys.route(id),
    queryFn: () => fetchRoute(id),
  };
}

function searchOptions(params: SearchQueryParams = {}) {
  const normalized = normalizeSearchQueryParams(params);
  return {
    queryKey: queryKeys.search(normalized),
    queryFn: async () => await fetchSearchAll(normalized),
    enabled: normalized.q.length > 0,
  };
}

export function useRegionsQuery(params: ListQueryParams = {}) {
  return useSuspenseQuery(regionsOptions(params));
}

export function useRegionQuery(idOrCode: string) {
  return useSuspenseQuery(regionOptions(idOrCode));
}

export function useStationsQuery(params: ListQueryParams = {}) {
  return useSuspenseQuery(stationsOptions(params));
}

export function useStationQuery(idOrCode: string) {
  return useSuspenseQuery(stationOptions(idOrCode));
}

export function useRoutesQuery(params: ListQueryParams = {}) {
  return useSuspenseQuery(routesOptions(params));
}

export function useRouteQuery(idOrSlug: string) {
  return useSuspenseQuery(routeOptions(idOrSlug));
}

export function useSearchQuery(params: SearchQueryParams = {}) {
  return useQuery(searchOptions(params));
}
