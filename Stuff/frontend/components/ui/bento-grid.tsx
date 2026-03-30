// https://magicui.design/docs/components/bento-grid

import { ArrowRightIcon } from "@radix-ui/react-icons";
import type { ComponentPropsWithoutRef, ReactNode } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface BentoGridProps extends ComponentPropsWithoutRef<"div"> {
  children: ReactNode;
  className?: string;
}

interface BentoCardProps extends ComponentPropsWithoutRef<"div"> {
  name: string;
  className: string;
  background?: ReactNode;
  Icon: React.ElementType;
  children: ReactNode;
  href?: string;
  cta?: string;
}

const BentoGrid = ({ children, className, ...props }: BentoGridProps) => {
  return (
    <div
      className={cn("grid w-full grid-cols-3 gap-4", className)}
      style={{ gridAutoRows: "minmax(22rem, auto)" }}
      {...props}
    >
      {children}
    </div>
  );
};

const BentoCard = ({
  name,
  className,
  background,
  Icon,
  children,
  href,
  cta,
  ...props
}: BentoCardProps) => (
  <div
    key={name}
    className={cn(
      "group relative col-span-3 flex flex-col overflow-hidden rounded-xl",
      // light styles
      "bg-background [box-shadow:0_0_0_1px_rgba(0,0,0,.03),0_2px_4px_rgba(0,0,0,.05),0_12px_24px_rgba(0,0,0,.05)]",
      // dark styles
      "transform-gpu dark:bg-background dark:[border:1px_solid_rgba(255,255,255,.1)] dark:[box-shadow:0_-20px_80px_-20px_#ffffff1f_inset]",
      className,
    )}
    {...props}
  >
    <div>{background}</div>
    <div className="flex flex-1 flex-col justify-end p-4">
      <div className="pointer-events-none z-10 flex transform-gpu flex-col gap-1 transition-all duration-300">
        <Icon className="h-8 w-8 origin-left transform-gpu text-neutral-700 transition-all duration-300 ease-in-out group-hover:scale-75" />
        <h3 className="font-semibold text-lg text-neutral-700 dark:text-neutral-300">
          {name}
        </h3>
        <div className="pointer-events-auto max-w-lg text-neutral-400">
          {children}
        </div>
      </div>

      <div
        className={cn(
          "pointer-events-none flex w-full translate-y-0 transform-gpu flex-row items-center transition-all duration-300 group-hover:translate-y-0 group-hover:opacity-100 lg:hidden",
        )}
      >
        {href && (
          <Button
            variant="link"
            asChild
            size="sm"
            className="pointer-events-auto p-0"
          >
            <Link to={href}>
              {cta}
              <ArrowRightIcon className="ms-2 h-4 w-4 rtl:rotate-180" />
            </Link>
          </Button>
        )}
      </div>
    </div>

    <div
      className={cn(
        "pointer-events-none absolute top-0 right-0 hidden translate-x-10 transform-gpu flex-row items-center p-4 opacity-0 transition-all duration-300 group-hover:translate-x-0 group-hover:opacity-100 lg:flex",
      )}
    >
      {href && (
        <Button
          variant="link"
          asChild
          size="sm"
          className="pointer-events-auto p-0"
        >
          <Link to={href}>
            {cta}
            <ArrowRightIcon className="ms-2 h-4 w-4 rtl:rotate-180" />
          </Link>
        </Button>
      )}
    </div>

    <div
      className="pointer-events-none absolute inset-0 transform-gpu transition-all duration-300 group-hover:bg-black/3 group-hover:dark:bg-neutral-800/10"
      style={{ pointerEvents: "none" }}
    />
  </div>
);

export { BentoCard, BentoGrid };
