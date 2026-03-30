interface PageHeaderProps {
  title: string;
  imageUrl?: string | null;
  imageAlt?: string;
  imageAspect?: "video" | "21/9";
}

export function PageHeader({
  title,
  imageUrl,
  imageAlt,
  imageAspect = "video",
}: PageHeaderProps) {
  return (
    <>
      <h1 className="mb-8 font-bold text-4xl">{title}</h1>
      <div
        className={`mb-8 w-full overflow-hidden rounded-xl ${
          imageAspect === "21/9"
            ? "aspect-21/9 max-h-[300px] md:max-h-[400px]"
            : "aspect-video"
        }`}
      >
        {imageUrl && (
          <img
            src={imageUrl}
            alt={imageAlt ?? title}
            className="h-full w-full object-cover object-center"
          />
        )}
      </div>
    </>
  );
}
