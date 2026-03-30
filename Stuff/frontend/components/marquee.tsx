import type { LucideIcon } from "lucide-react";
import { MapIcon, MapPinIcon, RouteIcon } from "lucide-react";
import { Link } from "react-router-dom";
import { Marquee } from "@/components/ui/marquee";
import { cn } from "@/lib/utils";

const navLinks = [
  { href: "/stations", icon: MapPinIcon, label: "Stations" },
  { href: "/routes", icon: RouteIcon, label: "Routes" },
  { href: "/regions", icon: MapIcon, label: "Regions" },
];

const NavLink = ({
  href,
  icon: Icon,
  label,
}: {
  href: string;
  icon: LucideIcon;
  label: string;
}) => {
  return (
    <Link
      to={href}
      className={cn(
        "relative flex h-full w-48 cursor-pointer items-center gap-3 overflow-hidden rounded-xl border p-4 transition-colors",
        "border-gray-950/10 bg-gray-950/1 hover:bg-gray-950/5",
        "dark:border-gray-50/10 dark:bg-gray-50/10 dark:hover:bg-gray-50/15",
      )}
    >
      <Icon className="size-6 shrink-0" />
      <span className="font-medium text-base">{label}</span>
    </Link>
  );
};

export function MarqueeDemo() {
  return (
    <div className="relative flex w-full flex-col items-center justify-center gap-2 overflow-hidden">
      <Marquee pauseOnHover className="[--duration:15s]">
        {navLinks.map((link) => (
          <NavLink key={link.label} {...link} />
        ))}
      </Marquee>
      <Marquee pauseOnHover reverse className="[--duration:15s]">
        {navLinks.map((link) => (
          <NavLink key={link.label} {...link} />
        ))}
      </Marquee>
      <div className="pointer-events-none absolute inset-y-0 left-0 w-1/4 bg-linear-to-r from-background"></div>
      <div className="pointer-events-none absolute inset-y-0 right-0 w-1/4 bg-linear-to-l from-background"></div>
    </div>
  );
}
