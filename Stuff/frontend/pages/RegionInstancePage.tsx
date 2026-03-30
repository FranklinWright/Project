import {
  AlertCircle,
  Bus,
  Car,
  DollarSign,
  Hash,
  Link2,
  MapPin,
  TrainTrack,
  Users,
} from "lucide-react";
import { Suspense } from "react";
import { useParams } from "react-router-dom";
import {
  buildLinkItem,
  OfficialLinks,
  PageHeader,
  PageHeaderSkeleton,
  RouteCard,
  SectionWithGrid,
  StationCard,
} from "@/components/cards";
import { BentoCard, BentoGrid } from "@/components/ui/bento-grid";
import { formatCurrency, formatPercent, formatPopulation } from "@/lib/format";
import { useRegionQuery } from "@/lib/queries";
import { hasItems, hasValue } from "@/lib/utils";

function RegionStatsCards({
  region,
}: {
  region: NonNullable<ReturnType<typeof useRegionQuery>["data"]>;
}) {
  const officialLinks = [
    buildLinkItem(region.wikipediaUrl, "Wikipedia", "purple"),
    buildLinkItem(region.tourismUrl, "Official Tourism Site", "green"),
    buildLinkItem(region.twitterUrl, "Twitter / X", "sky"),
  ].filter((l): l is NonNullable<typeof l> => l != null);

  return (
    <BentoGrid>
      {hasValue(region.railroadsOverview) && (
        <BentoCard
          Icon={TrainTrack}
          name="Railroads Overview"
          className="col-span-3 **:max-w-none lg:col-span-3"
        >
          <p className="whitespace-pre-line">{region.railroadsOverview}</p>
        </BentoCard>
      )}
      {hasValue(region.population) && (
        <BentoCard
          Icon={Users}
          name="Population"
          className="col-span-3 lg:col-span-1"
        >
          {formatPopulation(region.population)}
        </BentoCard>
      )}
      {hasValue(region.medianHouseholdIncome) && (
        <BentoCard
          Icon={DollarSign}
          name="Median Household Income"
          className="col-span-3 lg:col-span-1"
        >
          {formatCurrency(region.medianHouseholdIncome)}
        </BentoCard>
      )}
      {hasValue(region.noVehicleAvailablePercent) && (
        <BentoCard
          Icon={Car}
          name="No Vehicle Access"
          className="col-span-3 lg:col-span-1"
        >
          {formatPercent(region.noVehicleAvailablePercent)}
        </BentoCard>
      )}
      {hasValue(region.numberOfAmtrakStations) && (
        <BentoCard
          Icon={MapPin}
          name="Number of Amtrak Stations"
          className="col-span-3 lg:col-span-1"
        >
          {region.numberOfAmtrakStations}
        </BentoCard>
      )}
      {hasValue(region.numberOfAmtrakRoutes) && (
        <BentoCard
          Icon={Hash}
          name="Number of Amtrak Routes"
          className="col-span-3 lg:col-span-1"
        >
          {region.numberOfAmtrakRoutes}
        </BentoCard>
      )}
      {hasValue(region.povertyRatePercent) && (
        <BentoCard
          Icon={AlertCircle}
          name="Poverty Rate"
          className="col-span-3 lg:col-span-1"
        >
          {formatPercent(region.povertyRatePercent)}
        </BentoCard>
      )}
      {hasItems(region.publicTransportationToWork) ? (
        <BentoCard
          Icon={Bus}
          name="Public Transit Providers"
          className="col-span-3 lg:col-span-2"
        >
          <ul className="list-inside list-disc">
            {region.publicTransportationToWork.map((provider) => (
              <li key={provider}>{provider}</li>
            ))}
          </ul>
        </BentoCard>
      ) : null}
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

function RegionHeaderAndStats({ id }: { id: string }) {
  const region = useRegionQuery(id).data;

  if (!region) {
    return (
      <div className="m-4 rounded-lg bg-red-100 p-8 text-center text-red-800">
        Region &quot;{id}&quot; not found.
      </div>
    );
  }

  return (
    <>
      <PageHeader
        title={region.name}
        imageUrl={region.imageUrl}
        imageAlt={region.name}
        imageAspect="video"
      />
      <RegionStatsCards region={region} />
    </>
  );
}

function RegionStationsSection({
  region,
}: {
  region: NonNullable<ReturnType<typeof useRegionQuery>["data"]>;
}) {
  const linkedStations = region.linkedStations ?? [];
  if (linkedStations.length === 0) return null;

  return (
    <SectionWithGrid title="Amtrak Stations">
      {linkedStations.map((station) => (
        <StationCard key={station.code} station={station} />
      ))}
    </SectionWithGrid>
  );
}

function RegionRoutesSection({
  region,
}: {
  region: NonNullable<ReturnType<typeof useRegionQuery>["data"]>;
}) {
  const linkedRoutes = region.linkedRoutes ?? [];
  if (linkedRoutes.length === 0) return null;

  return (
    <SectionWithGrid title="Passing Routes">
      {linkedRoutes.map((route) => (
        <RouteCard key={route.name} route={route} />
      ))}
    </SectionWithGrid>
  );
}

function RegionLinkedSections({
  region,
}: {
  region: NonNullable<ReturnType<typeof useRegionQuery>["data"]>;
}) {
  return (
    <>
      <RegionStationsSection region={region} />
      <RegionRoutesSection region={region} />
    </>
  );
}

export function RegionInstancePage() {
  const { id } = useParams();
  if (!id) return <div className="p-8 text-center">Invalid region.</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <Suspense fallback={<PageHeaderSkeleton />}>
        <RegionPageContent id={id} />
      </Suspense>
    </div>
  );
}

function RegionPageContent({ id }: { id: string }) {
  const region = useRegionQuery(id).data;
  if (!region) {
    return (
      <div className="m-4 rounded-lg bg-red-100 p-8 text-center text-red-800">
        Region &quot;{id}&quot; not found.
      </div>
    );
  }
  return (
    <>
      <RegionHeaderAndStats id={id} />
      <RegionLinkedSections region={region} />
    </>
  );
}
