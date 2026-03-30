import { TrainFront } from "lucide-react";
import { Link } from "react-router-dom";
import type { Station } from "@/types/api";
import { CardField, CardFieldList } from "./CardFieldList";
import { ImageEntityCard } from "./ImageEntityCard";

interface StationCardProps {
  station: Station;
}

export function StationCard({ station }: StationCardProps) {
  return (
    <ImageEntityCard
      Icon={TrainFront}
      name={`${station.name} (${station.code})`}
      imageUrl={station.imageUrl}
      imageAlt={station.name}
      href={`/stations/${station.code}`}
    >
      <div className="flex flex-col gap-1">
        <CardFieldList>
          <CardField label="Hours:">{station.hours}</CardField>
          <CardField label="Timezone:">{station.timezone}</CardField>
          <CardField label="Routes Served Count:">
            {station.routesServedCount}
          </CardField>
          <CardField label="ADA Accessible:">Yes</CardField>
          {station.regionCode && (
            <CardField label="Region:">
              <Link
                className="text-blue-400 underline decoration-1 decoration-blue-400 underline-offset-2 transition-colors hover:text-blue-300"
                to={`/regions/${station.regionCode}`}
              >
                {station.regionCode}
              </Link>
            </CardField>
          )}
        </CardFieldList>
      </div>
    </ImageEntityCard>
  );
}
