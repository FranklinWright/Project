import { Route as RouteIcon } from "lucide-react";
import { Link } from "react-router-dom";
import { highlightText } from "@/lib/highlight";
import type { Route } from "@/types/api";
import { CardField, CardFieldList } from "./CardFieldList";
import { ImageEntityCard } from "./ImageEntityCard";

interface RouteCardProps {
  route: Route;
  highlightQuery?: string;
}

export function RouteCard({ route, highlightQuery }: RouteCardProps) {
  return (
    <ImageEntityCard
      Icon={RouteIcon}
      name={highlightText(route.name, highlightQuery)}
      imageUrl={route.imageUrl}
      imageAlt={route.name}
      href={`/routes/${route.name.replace(/\s+/g, "-").toLowerCase()}`}
    >
      <div className="flex flex-col gap-1">
        <CardFieldList>
          <CardField label="Stations Served:">{route.stationsServed}</CardField>
          <CardField label="Travel Time:">{route.travelTimeInHours}</CardField>
          <CardField label="Major Stops:">
            {highlightText(route.majorStops?.join(", "), highlightQuery)}
          </CardField>
          <CardField label="Menu:">
            {highlightText(route.menu?.join(", "), highlightQuery)}
          </CardField>
          <CardField label="Regions Spanned:">
            {(route.regionsSpanned ?? []).map((regionCode, idx, arr) => (
              <span key={regionCode}>
                <Link
                  to={`/regions/${regionCode}`}
                  className="text-blue-400 underline decoration-1 decoration-blue-400 underline-offset-2 transition-colors hover:text-blue-300"
                >
                  {highlightText(regionCode, highlightQuery)}
                </Link>
                {idx < arr.length - 1 && ", "}
              </span>
            ))}
          </CardField>
        </CardFieldList>
      </div>
    </ImageEntityCard>
  );
}
