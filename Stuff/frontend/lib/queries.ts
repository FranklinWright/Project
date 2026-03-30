import { useSuspenseQuery } from "@tanstack/react-query";
import {
  fetchRegion,
  fetchRegions,
  fetchRoute,
  fetchRoutes,
  fetchStation,
  fetchStations,
  type ListQueryParams,
} from "./api";

const DEFAULT_PAGE = 1;
const DEFAULT_PAGE_SIZE = 24;

function normalizeListQueryParams(params: ListQueryParams = {}) {
  return {
    page: Math.max(1, params.page ?? DEFAULT_PAGE),
    pageSize: Math.max(1, params.pageSize ?? DEFAULT_PAGE_SIZE),
  };
}

export const queryKeys = {
  regions: (page = DEFAULT_PAGE, pageSize = DEFAULT_PAGE_SIZE) =>
    ["regions", page, pageSize] as const,
  region: (idOrCode: string) => ["regions", idOrCode] as const,
  stations: (page = DEFAULT_PAGE, pageSize = DEFAULT_PAGE_SIZE) =>
    ["stations", page, pageSize] as const,
  station: (idOrCode: string) => ["stations", idOrCode] as const,
  routes: (page = DEFAULT_PAGE, pageSize = DEFAULT_PAGE_SIZE) =>
    ["routes", page, pageSize] as const,
  route: (idOrSlug: string) => ["routes", idOrSlug] as const,
  aboutMemberCommits: (gitlabUsername: string) =>
    ["about", "stats", "member", gitlabUsername, "commits"] as const,
  aboutMemberIssues: (gitlabUsername: string) =>
    ["about", "stats", "member", gitlabUsername, "issues"] as const,
};

function regionsOptions(params: ListQueryParams = {}) {
  const normalized = normalizeListQueryParams(params);

  return {
    queryKey: queryKeys.regions(normalized.page, normalized.pageSize),
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
    queryKey: queryKeys.stations(normalized.page, normalized.pageSize),
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
    queryKey: queryKeys.routes(normalized.page, normalized.pageSize),
    queryFn: async () => await fetchRoutes(normalized),
  };
}

function routeOptions(id: string) {
  return {
    queryKey: queryKeys.route(id),
    queryFn: () => fetchRoute(id),
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
