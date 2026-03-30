import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { BentoCard } from "@/components/ui/bento-grid";

interface ImageEntityCardProps {
  name: string;
  imageUrl?: string | null;
  imageAlt?: string;
  href: string;
  Icon: LucideIcon;
  children: ReactNode;
}

export function ImageEntityCard({
  name,
  imageUrl,
  imageAlt,
  href,
  Icon,
  children,
}: ImageEntityCardProps) {
  return (
    <BentoCard
      href={href}
      Icon={Icon}
      name={name}
      cta="View Details"
      className="col-span-3 h-88 text-white shadow-none transition-transform duration-300 ease-in-out hover:scale-103 hover:shadow-lg lg:col-span-1 [&_a]:text-white! [&_h3]:text-white! [&_svg]:text-white!"
      background={
        <div className="absolute inset-0 h-full w-full transition-opacity duration-300">
          <img
            className="h-full w-full object-cover"
            src={imageUrl ?? ""}
            alt={imageAlt ?? name}
          />
          <div className="absolute inset-0 bg-black/60" />
        </div>
      }
    >
      <div className="mt-2 flex h-full flex-col gap-2 rounded-md transition-colors duration-300">
        {children}
      </div>
    </BentoCard>
  );
}
