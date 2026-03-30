export interface Station {
  name: string;
  code: string;
  address: string;
  timezone: string;
  description: string;
  hours: string;
  nearbyStations: string[];
  pointsOfInterest: string[];
  connectedDestinations: string[];
  routesServedCount: number;
  imageUrl: string;
  regionId: string | number;
  amtrakUrl: string;
  wikipediaUrl: string;
  facebookUrl?: string;
  twitterUrl?: string;
  poiImageUrl: string;
  poiImageLabel: string;
  history: string;
}

export interface Route {
  name: string;
  majorStops: string[];
  description: string;
  menu: string[];
  travelTimeInHours: string;
  regionsSpanned: string;
  stationsServed: number;
  imageUrl: string;
  amtrakUrl: string;
  wikipediaUrl: string;
  youtubeUrl?: string;
}

export interface Region {
  name: string;
  code: string;
  population: string;
  medianHouseholdIncome: string;
  noVehicleAvailable: string;
  povertyStatus: string;
  publicTransportationToWork: string[];
  imageUrl: string;
  wikipediaUrl: string;
  tourismUrl: string;
  twitterUrl?: string;
  railroadsOverview: string;
  numberOfAmtrakStations: number;
  numberOfAmtrakRoutes: number;
}
