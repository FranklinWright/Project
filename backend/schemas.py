"""Pydantic schemas for API validation and serialization. Used by pydantic2ts for TypeScript generation."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PaginationLinks(BaseModel):
    """Links for paginated responses."""

    model_config = ConfigDict(populate_by_name=True)

    self_link: str = Field(alias="self")
    next_link: str | None = Field(None, alias="next")
    previous: str | None = None
    first: str = Field(alias="first")
    last: str = Field(alias="last")


class Pagination(BaseModel):
    """Pagination metadata."""

    model_config = ConfigDict(populate_by_name=True)

    total_items: int = Field(alias="totalItems")
    total_pages: int = Field(alias="totalPages")
    current_page: int = Field(alias="currentPage")
    page_size: int = Field(alias="pageSize")
    has_next_page: bool = Field(alias="hasNextPage")
    has_previous_page: bool = Field(alias="hasPreviousPage")
    links: PaginationLinks


class Region(BaseModel):
    """Region model schema."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    code: str
    population: int | None = None
    median_household_income: int | None = Field(None, alias="medianHouseholdIncome")
    no_vehicle_available_percent: float | None = Field(
        None, alias="noVehicleAvailablePercent"
    )
    poverty_rate_percent: float | None = Field(None, alias="povertyRatePercent")
    public_transportation_to_work: list[str] = Field(
        default_factory=list, alias="publicTransportationToWork"
    )
    image_url: str | None = Field(None, alias="imageUrl")
    wikipedia_url: str | None = Field(None, alias="wikipediaUrl")
    tourism_url: str | None = Field(None, alias="tourismUrl")
    twitter_url: str | None = Field(None, alias="twitterUrl")
    railroads_overview: str | None = Field(None, alias="railroadsOverview")
    number_of_amtrak_stations: int | None = Field(None, alias="numberOfAmtrakStations")
    number_of_amtrak_routes: int | None = Field(None, alias="numberOfAmtrakRoutes")
    updated_at: str | None = Field(None, alias="updatedAt")
    linked_stations: list["Station"] | None = Field(None, alias="linkedStations")
    linked_routes: list["Route"] | None = Field(None, alias="linkedRoutes")


class RegionsListResponse(BaseModel):
    """Paginated regions list response."""

    model_config = ConfigDict(populate_by_name=True)

    data: list[Region]
    pagination: Pagination


class Station(BaseModel):
    """Station model schema."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    code: str
    address: str | None = None
    timezone: str | None = None
    description: str | None = None
    hours: str | None = None
    nearby_stations: list[str] = Field(default_factory=list, alias="nearbyStations")
    points_of_interest: list[str] = Field(
        default_factory=list, alias="pointsOfInterest"
    )
    connected_destinations: list[str] = Field(
        default_factory=list, alias="connectedDestinations"
    )
    image_url: str | None = Field(None, alias="imageUrl")
    region_id: int | None = Field(None, alias="regionId")
    region_code: str | None = Field(None, alias="regionCode")
    routes_served_count: int | None = Field(None, alias="routesServedCount")
    amtrak_url: str | None = Field(None, alias="amtrakUrl")
    wikipedia_url: str | None = Field(None, alias="wikipediaUrl")
    facebook_url: str | None = Field(None, alias="facebookUrl")
    twitter_url: str | None = Field(None, alias="twitterUrl")
    poi_image_url: str | None = Field(None, alias="poiImageUrl")
    poi_image_label: str | None = Field(None, alias="poiImageLabel")
    history: str | None = None
    updated_at: str | None = Field(None, alias="updatedAt")
    linked_routes: list["Route"] | None = Field(None, alias="linkedRoutes")
    linked_region: Optional["Region"] = Field(None, alias="linkedRegion")


class StationsListResponse(BaseModel):
    """Paginated stations list response."""

    model_config = ConfigDict(populate_by_name=True)

    data: list[Station]
    pagination: Pagination


class Route(BaseModel):
    """Route model schema."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    major_stops: list[str] = Field(default_factory=list, alias="majorStops")
    description: str | None = None
    menu: list[str] = Field(default_factory=list)
    travel_time_in_hours: str | None = Field(None, alias="travelTimeInHours")
    regions_spanned: list[str] = Field(default_factory=list, alias="regionsSpanned")
    stations_served: int | None = Field(None, alias="stationsServed")
    image_url: str | None = Field(None, alias="imageUrl")
    amtrak_url: str | None = Field(None, alias="amtrakUrl")
    wikipedia_url: str | None = Field(None, alias="wikipediaUrl")
    youtube_url: str | None = Field(None, alias="youtubeUrl")
    updated_at: str | None = Field(None, alias="updatedAt")
    linked_stations: list["Station"] | None = Field(None, alias="linkedStations")
    linked_regions: list["Region"] | None = Field(None, alias="linkedRegions")


class RoutesListResponse(BaseModel):
    """Paginated routes list response."""

    model_config = ConfigDict(populate_by_name=True)

    data: list[Route]
    pagination: Pagination


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str


# Resolve forward references for nested schemas
Region.model_rebuild()
Station.model_rebuild()
Route.model_rebuild()
