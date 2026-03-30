interface LinkItem {
  href: string;
  label: string;
  colorClass?: string;
}

interface OfficialLinksProps {
  links: LinkItem[];
}

const COLOR_MAP = {
  blue: "bg-blue-600/20 text-blue-400 hover:bg-blue-600/30",
  purple: "bg-purple-600/20 text-purple-400 hover:bg-purple-600/30",
  green: "bg-green-600/20 text-green-400 hover:bg-green-600/30",
  red: "bg-red-600/20 text-red-400 hover:bg-red-600/30",
  sky: "bg-sky-600/20 text-sky-400 hover:bg-sky-600/30",
  indigo: "bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600/30",
} as const;

export function OfficialLinks({ links }: OfficialLinksProps) {
  return (
    <div className="flex flex-col gap-2">
      {links
        .filter((l) => l.href && l.href !== "#")
        .map((link) => (
          <a
            key={link.label}
            href={link.href}
            target="_blank"
            rel="noopener noreferrer"
            className={`pointer-events-auto inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-sm transition-colors ${
              link.colorClass ?? COLOR_MAP.blue
            }`}
          >
            {link.label}
          </a>
        ))}
    </div>
  );
}

export function buildLinkItem(
  href: string | null | undefined,
  label: string,
  color: keyof typeof COLOR_MAP = "blue",
): LinkItem | null {
  if (!href) return null;
  return { href, label, colorClass: COLOR_MAP[color] };
}
