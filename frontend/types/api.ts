/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

/**
 * Error response schema.
 */
export interface ErrorResponse {
  error: string;
}
/**
 * Pagination metadata.
 */
export interface Pagination {
  totalItems: number;
  totalPages: number;
  currentPage: number;
  pageSize: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  links: PaginationLinks;
}
/**
 * Links for paginated responses.
 */
export interface PaginationLinks {
  self: string;
  next?: string | null;
  previous?: string | null;
  first: string;
  last: string;
}
/**
 * Region model schema.
 */
export interface Region {
  id: number;
  name: string;
  code: string;
  population?: number | null;
  medianHouseholdIncome?: number | null;
  noVehicleAvailablePercent?: number | null;
  povertyRatePercent?: number | null;
  publicTransportationToWork?: string[];
  imageUrl?: string | null;
  wikipediaUrl?: string | null;
  tourismUrl?: string | null;
  twitterUrl?: string | null;
  railroadsOverview?: string | null;
  numberOfAmtrakStations?: number | null;
  numberOfAmtrakRoutes?: number | null;
  updatedAt?: string | null;
  linkedStations?: Station[] | null;
  linkedRoutes?: Route[] | null;
}
/**
 * Station model schema.
 */
export interface Station {
  id: number;
  name: string;
  code: string;
  address?: string | null;
  timezone?: string | null;
  description?: string | null;
  hours?: string | null;
  nearbyStations?: string[];
  pointsOfInterest?: string[];
  connectedDestinations?: string[];
  imageUrl?: string | null;
  regionId?: number | null;
  regionCode?: string | null;
  routesServedCount?: number | null;
  amtrakUrl?: string | null;
  wikipediaUrl?: string | null;
  facebookUrl?: string | null;
  twitterUrl?: string | null;
  poiImageUrl?: string | null;
  poiImageLabel?: string | null;
  history?: string | null;
  updatedAt?: string | null;
  linkedRoutes?: Route[] | null;
  linkedRegion?: Region | null;
}
/**
 * Route model schema.
 */
export interface Route {
  id: number;
  name: string;
  majorStops?: string[];
  description?: string | null;
  menu?: string[];
  travelTimeInHours?: string | null;
  regionsSpanned?: string[];
  stationsServed?: number | null;
  imageUrl?: string | null;
  amtrakUrl?: string | null;
  wikipediaUrl?: string | null;
  youtubeUrl?: string | null;
  updatedAt?: string | null;
  linkedStations?: Station[] | null;
  linkedRegions?: Region[] | null;
}
/**
 * Paginated regions list response.
 */
export interface RegionsListResponse {
  data: Region[];
  pagination: Pagination;
}
/**
 * Paginated routes list response.
 */
export interface RoutesListResponse {
  data: Route[];
  pagination: Pagination;
}
/**
 * Paginated stations list response.
 */
export interface StationsListResponse {
  data: Station[];
  pagination: Pagination;
}
