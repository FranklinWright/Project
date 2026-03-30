import {
  Clock,
  Compass,
  ExternalLink,
  Globe,
  Hash,
  Info,
  Landmark,
  Link2,
  MapPin,
  TentTree,
} from "lucide-react";
import { Suspense } from "react";
import { useParams } from "react-router-dom";
import {
  buildLinkItem,
  OfficialLinks,
  PageHeader,
  PageHeaderSkeleton,
  RegionCard,
  RouteCard,
  SectionWithGrid,
} from "@/components/cards";
import { BentoCard, BentoGrid } from "@/components/ui/bento-grid";
import { useStationQuery } from "@/lib/queries";
import { hasItems, hasValue } from "@/lib/utils";

function StationDetailsCards({ id }: { id: string }) {
  const station = useStationQuery(id).data;

  if (!station) return null;

  const officialLinks = [
    buildLinkItem(station.amtrakUrl, "Amtrak Station Page", "blue"),
    buildLinkItem(station.wikipediaUrl, "Wikipedia", "purple"),
    buildLinkItem(station.facebookUrl, "Facebook", "indigo"),
    buildLinkItem(station.twitterUrl, "Twitter / X", "sky"),
  ].filter((l): l is NonNullable<typeof l> => l != null);

  return (
    <BentoGrid>
      {hasValue(station.description) && (
        <BentoCard
          Icon={Info}
          name="Description"
          className="col-span-3 lg:col-span-2"
        >
          {station.description}
        </BentoCard>
      )}
      {hasValue(station.hours) && (
        <BentoCard
          Icon={Clock}
          name="Hours"
          className="col-span-3 lg:col-span-1"
        >
          {station.hours}
        </BentoCard>
      )}
      {hasValue(station.address) && (
        <BentoCard
          Icon={MapPin}
          name="Location"
          className="col-span-3 lg:col-span-1"
        >
          <div className="flex flex-col gap-2">
            <p className="line-clamp-2 text-sm">{station.address}</p>
            <div className="relative z-10 h-[180px] w-full overflow-hidden rounded-lg border bg-muted">
              <iframe
                title={`Map for ${station.name}`}
                width="100%"
                height="100%"
                style={{ border: 0, pointerEvents: "auto" }}
                src={`https://www.google.com/maps?q=${encodeURIComponent(
                  station.address ?? "",
                )}&z=14&output=embed`}
                allowFullScreen
              />
            </div>
          </div>
        </BentoCard>
      )}
      {hasItems(station.pointsOfInterest) && (
        <BentoCard
          Icon={TentTree}
          name="Points of Interest"
          className="col-span-3 lg:col-span-1"
        >
          <div className="flex flex-col gap-3">
            <ul className="list-inside list-disc">
              {station.pointsOfInterest?.map((poi) => (
                <li key={poi}>{poi}</li>
              ))}
            </ul>
            {station.poiImageUrl && (
              <div className="overflow-hidden rounded-lg">
                <img
                  src={station.poiImageUrl}
                  alt={station.poiImageLabel ?? ""}
                  className="h-32 w-full object-cover"
                />
                <p className="mt-1 text-center text-muted-foreground text-xs">
                  {station.poiImageLabel}
                </p>
              </div>
            )}
          </div>
        </BentoCard>
      )}
      {hasValue(station.timezone) && (
        <BentoCard
          Icon={Globe}
          name="Timezone"
          className="col-span-3 lg:col-span-1"
        >
          {station.timezone}
        </BentoCard>
      )}
      {hasItems(station.nearbyStations) && (
        <BentoCard
          Icon={ExternalLink}
          name="Nearby Stations"
          className="col-span-3 lg:col-span-1"
        >
          <ul className="list-inside list-disc">
            {station.nearbyStations?.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ul>
        </BentoCard>
      )}
      {hasItems(station.connectedDestinations) && (
        <BentoCard
          Icon={Compass}
          name="Connected Destinations"
          className="col-span-3 lg:col-span-1"
        >
          <ul className="list-inside list-disc">
            {station.connectedDestinations?.map((d) => (
              <li key={d}>{d}</li>
            ))}
          </ul>
        </BentoCard>
      )}
      {hasValue(station.routesServedCount) && (
        <BentoCard
          Icon={Hash}
          name="Routes Served Count"
          className="col-span-3 lg:col-span-1"
        >
          {station.routesServedCount}
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
      {hasValue(station.history) && (
        <BentoCard
          Icon={Landmark}
          name="History"
          className="col-span-3 **:max-w-none lg:col-span-3"
        >
          <p className="whitespace-pre-line">{station.history}</p>
        </BentoCard>
      )}
    </BentoGrid>
  );
}

function StationHeaderAndDetails({ id }: { id: string }) {
  const station = useStationQuery(id).data;

  if (!station) {
    return <div className="p-8 text-center">Station not found.</div>;
  }

  return (
    <>
      <PageHeader
        title={station.name}
        imageUrl={station.imageUrl}
        imageAlt={station.name}
      />
      <StationDetailsCards id={id} />
    </>
  );
}

function StationRoutesSection({
  station,
}: {
  station: NonNullable<ReturnType<typeof useStationQuery>["data"]>;
}) {
  const linkedRoutes = station.linkedRoutes ?? [];
  if (linkedRoutes.length === 0) return null;

  return (
    <SectionWithGrid title="Servicing Routes">
      {linkedRoutes.map((route) => (
        <RouteCard key={route.name} route={route} />
      ))}
    </SectionWithGrid>
  );
}

function StationRegionSection({
  region,
}: {
  region: NonNullable<
    ReturnType<typeof useStationQuery>["data"]
  >["linkedRegion"];
}) {
  if (!region) return null;

  return (
    <SectionWithGrid title="Region">
      <RegionCard region={region} />
    </SectionWithGrid>
  );
}

function StationLinkedSections({
  station,
}: {
  station: NonNullable<ReturnType<typeof useStationQuery>["data"]>;
}) {
  return (
    <>
      <StationRoutesSection station={station} />
      {station.linkedRegion && (
        <StationRegionSection region={station.linkedRegion} />
      )}
    </>
  );
}

export function StationInstancePage() {
  const { id } = useParams();
  if (!id) return <div className="p-8 text-center">Invalid station.</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <Suspense fallback={<PageHeaderSkeleton />}>
        <StationPageContent id={id} />
      </Suspense>
    </div>
  );
}

function StationPageContent({ id }: { id: string }) {
  const station = useStationQuery(id).data;
  if (!station) {
    return <div className="p-8 text-center">Station not found.</div>;
  }
  return (
    <>
      <StationHeaderAndDetails id={id} />
      <StationLinkedSections station={station} />
    </>
  );
}
