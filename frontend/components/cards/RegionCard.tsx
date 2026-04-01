import { Map as MapIcon } from "lucide-react";
import { formatCurrency, formatPercent, formatPopulation } from "@/lib/format";
import { highlightText } from "@/lib/highlight";
import type { Region } from "@/types/api";
import { CardField, CardFieldList } from "./CardFieldList";
import { ImageEntityCard } from "./ImageEntityCard";

interface RegionCardProps {
  region: Region;
  highlightQuery?: string;
}

export function RegionCard({ region, highlightQuery }: RegionCardProps) {
  return (
    <ImageEntityCard
      Icon={MapIcon}
      name={highlightText(region.name, highlightQuery)}
      imageUrl={region.imageUrl}
      imageAlt={region.name}
      href={`/regions/${region.code}`}
    >
      <div className="flex flex-col gap-1 border-neutral-200/20 border-t pt-2">
        <CardFieldList>
          <CardField label="Population:">
            {formatPopulation(region.population)}
          </CardField>
          <CardField label="Median Income:">
            {formatCurrency(region.medianHouseholdIncome)}
          </CardField>
          <CardField label="No Vehicle Access:">
            {formatPercent(region.noVehicleAvailablePercent)}
          </CardField>
          <CardField label="Poverty Rate:">
            {formatPercent(region.povertyRatePercent)}
          </CardField>
          <CardField label="Transit Providers:">
            {highlightText(
              region.publicTransportationToWork?.join(", "),
              highlightQuery,
            )}
          </CardField>
        </CardFieldList>
      </div>
    </ImageEntityCard>
  );
}
