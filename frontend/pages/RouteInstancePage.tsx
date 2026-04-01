import { Clock, Hash, Info, Link2, MapPin, Utensils } from "lucide-react";
import { Suspense } from "react";
import { useParams } from "react-router-dom";
import {
  buildLinkItem,
  OfficialLinks,
  PageHeader,
  PageHeaderSkeleton,
  RegionCard,
  SectionWithGrid,
  StationCard,
} from "@/components/cards";
import { BentoCard, BentoGrid } from "@/components/ui/bento-grid";
import { useRouteQuery } from "@/lib/queries";
import { hasItems, hasValue } from "@/lib/utils";

function RouteDetailsCards({ id }: { id: string }) {
  const route = useRouteQuery(id).data;

  if (!route) return null;

  const officialLinks = [
    buildLinkItem(route.amtrakUrl, "Amtrak Route Page", "blue"),
    buildLinkItem(route.wikipediaUrl, "Wikipedia", "purple"),
    buildLinkItem(route.youtubeUrl, "YouTube Video", "red"),
  ].filter((l): l is NonNullable<typeof l> => l != null);

  return (
    <BentoGrid className="lg:grid-rows-1">
      {hasValue(route.description) && (
        <BentoCard
          Icon={Info}
          name="About the Route"
          className="col-span-3 lg:col-span-2"
        >
          {route.description}
        </BentoCard>
      )}
      {hasValue(route.travelTimeInHours) && (
        <BentoCard
          Icon={Clock}
          name="Travel Time"
          className="col-span-3 lg:col-span-1"
        >
          {route.travelTimeInHours}
        </BentoCard>
      )}
      {hasItems(route.menu) && (
        <BentoCard
          Icon={Utensils}
          name="Dining Menu"
          className="col-span-3 lg:col-span-1"
        >
          <ul className="list-inside list-disc">
            {route.menu?.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </BentoCard>
      )}
      {hasValue(route.stationsServed) && (
        <BentoCard
          Icon={Hash}
          name="Stations Served"
          className="col-span-3 lg:col-span-1"
        >
          {route.stationsServed}
        </BentoCard>
      )}
      {hasItems(route.majorStops) && (
        <BentoCard
          Icon={MapPin}
          name="Major Stops"
          className="col-span-3 lg:col-span-2"
        >
          {route.majorStops?.join(", ")}
        </BentoCard>
      )}
      {officialLinks.length > 0 && (
        <BentoCard
          Icon={Link2}
          name="Official Links"
          className="col-span-3 lg:col-span-1"
        >
          <OfficialLinks links={officialLinks} />
        </BentoCard>
      )}
    </BentoGrid>
  );
}

function RouteHeaderAndDetails({ id }: { id: string }) {
  const route = useRouteQuery(id).data;

  if (!route) {
    return <div className="p-8 text-center">Route not found</div>;
  }

  return (
    <>
      <PageHeader
        title={route.name}
        imageUrl={route.imageUrl}
        imageAlt={route.name}
      />
      <RouteDetailsCards id={id} />
    </>
  );
}

function RouteStationsSection({
  route,
}: {
  route: NonNullable<ReturnType<typeof useRouteQuery>["data"]>;
}) {
  const linkedStations = route.linkedStations ?? [];
  if (linkedStations.length === 0) return null;

  return (
    <SectionWithGrid title="Major Stops (Stations)">
      {linkedStations.map((station) => (
        <StationCard key={station.code} station={station} />
      ))}
    </SectionWithGrid>
  );
}

function RouteRegionsSection({
  route,
}: {
  route: NonNullable<ReturnType<typeof useRouteQuery>["data"]>;
}) {
  const linkedRegions = route.linkedRegions ?? [];
  if (linkedRegions.length === 0) return null;

  return (
    <SectionWithGrid title="Regions Spanned">
      {linkedRegions.map((region) => (
        <RegionCard key={region.code} region={region} />
      ))}
    </SectionWithGrid>
  );
}

function RouteLinkedSections({
  route,
}: {
  route: NonNullable<ReturnType<typeof useRouteQuery>["data"]>;
}) {
  return (
    <>
      <RouteStationsSection route={route} />
      <RouteRegionsSection route={route} />
    </>
  );
}

export function RouteInstancePage() {
  const { id } = useParams();
  if (!id) return <div className="p-8 text-center">Invalid route.</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <Suspense fallback={<PageHeaderSkeleton />}>
        <RoutePageContent id={id} />
      </Suspense>
    </div>
  );
}

function RoutePageContent({ id }: { id: string }) {
  const route = useRouteQuery(id).data;
  if (!route) {
    return <div className="p-8 text-center">Route not found</div>;
  }
  return (
    <>
      <RouteHeaderAndDetails id={id} />
      <RouteLinkedSections route={route} />
    </>
  );
}
