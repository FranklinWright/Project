import { FlickeringGrid } from "@/components/ui/flickering-grid";

export function DotBackground({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative flex h-[33vh] w-full shrink-0 items-center justify-center overflow-hidden bg-background">
      <FlickeringGrid
        className="absolute inset-0 z-0"
        squareSize={4}
        gridGap={6}
        color="rgb(128, 128, 128)"
        maxOpacity={0.5}
        flickerChance={0.1}
      />
      {children}
    </div>
  );
}
