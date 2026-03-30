import { Route as RouteIcon } from "lucide-react";
import { Link } from "react-router-dom";
import type { Route } from "@/types/api";
import { CardField, CardFieldList } from "./CardFieldList";
import { ImageEntityCard } from "./ImageEntityCard";

interface RouteCardProps {
  route: Route;
}

export function RouteCard({ route }: RouteCardProps) {
  return (
    <ImageEntityCard
      Icon={RouteIcon}
      name={route.name}
      imageUrl={route.imageUrl}
      imageAlt={route.name}
      href={`/routes/${route.name.replace(/\s+/g, "-").toLowerCase()}`}
    >
      <div className="flex flex-col gap-1">
        <CardFieldList>
          <CardField label="Stations Served:">{route.stationsServed}</CardField>
          <CardField label="Travel Time:">{route.travelTimeInHours}</CardField>
          <CardField label="Major Stops:">
            {route.majorStops?.join(", ")}
          </CardField>
          <CardField label="Menu:">{route.menu?.join(", ")}</CardField>
          <CardField label="Regions Spanned:">
            {(route.regionsSpanned ?? []).map((regionCode, idx, arr) => (
              <span key={regionCode}>
                <Link
                  to={`/regions/${regionCode}`}
                  className="text-blue-400 underline decoration-1 decoration-blue-400 underline-offset-2 transition-colors hover:text-blue-300"
                >
                  {regionCode}
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
