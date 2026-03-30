import {
  AccessibilityIcon,
  HomeIcon,
  InfoIcon,
  MapIcon,
  MapPinIcon,
  RouteIcon,
} from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { buttonVariants } from "@/components/ui/button";
import { Dock, DockIcon } from "@/components/ui/dock";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", icon: HomeIcon, label: "Home" },
  { href: "/stations", icon: MapPinIcon, label: "Stations" },
  { href: "/routes", icon: RouteIcon, label: "Routes" },
  { href: "/regions", icon: MapIcon, label: "Regions" },
  { href: "/about", icon: InfoIcon, label: "About" },
];

export function DockDemo() {
  const [showPanel, setShowPanel] = useState(false);
  const [highContrast, setHighContrast] = useState(false);

  function toggleContrast() {
    const next = !highContrast;
    setHighContrast(next);
    document.documentElement.classList.toggle("high-contrast", next);
  }

  return (
    <div className="fixed bottom-4 left-1/2 z-50 -translate-x-1/2">
      {showPanel && (
        <div className="mb-3 rounded-xl border border-border bg-background/80 p-4 shadow-lg backdrop-blur-md">
          <div className="flex items-center justify-between gap-4">
            <span className="font-medium text-sm">
              Accessibility (Contrast){" "}
            </span>
            <button
              type="button"
              role="switch"
              aria-checked={highContrast}
              onClick={toggleContrast}
              className={cn(
                "relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors",
                highContrast ? "bg-primary" : "bg-muted",
              )}
            >
              <span
                className={cn(
                  "pointer-events-none block size-5 rounded-full bg-white shadow-lg ring-0 transition-transform",
                  highContrast ? "translate-x-5" : "translate-x-0",
                )}
              />
            </button>
          </div>
        </div>
      )}
      <TooltipProvider>
        <Dock
          direction="middle"
          className="gap-6 rounded-3xl border border-gray-800 bg-zinc-900 p-4 px-6 py-4 shadow-xl"
        >
          {NAV_ITEMS.map((item) => (
            <DockIcon key={item.label}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Link
                    to={item.href}
                    aria-label={item.label}
                    className={cn(
                      buttonVariants({ variant: "ghost", size: "icon" }),
                      "size-14 rounded-xl text-white/90 transition-all hover:bg-zinc-700 active:scale-95",
                    )}
                  >
                    <item.icon className="size-7 stroke-[1.5]" />
                  </Link>
                </TooltipTrigger>
                <TooltipContent sideOffset={12}>
                  <p className="font-semibold text-xs">{item.label}</p>
                </TooltipContent>
              </Tooltip>
            </DockIcon>
          ))}
          <DockIcon>
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  aria-label="Accessible Mode"
                  onClick={() => setShowPanel((v) => !v)}
                  className={cn(
                    buttonVariants({ variant: "ghost", size: "icon" }),
                    "size-14 rounded-xl text-white/90 transition-all hover:bg-zinc-700 active:scale-95",
                  )}
                >
                  <AccessibilityIcon className="size-7 stroke-[1.5] text-white" />
                </button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Accessible Mode</p>
              </TooltipContent>
            </Tooltip>
          </DockIcon>
        </Dock>
      </TooltipProvider>
    </div>
  );
}
