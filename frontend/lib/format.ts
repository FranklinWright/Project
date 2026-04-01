export function formatPopulation(n: number | null | undefined): string {
  if (n == null) return "";
  if (n >= 1_000_000) {
    return `${(n / 1_000_000).toFixed(1)} million`;
  }
  if (n >= 1_000) {
    return `${(n / 1_000).toFixed(1)} thousand`;
  }
  return String(n);
}

export function formatCurrency(n: number | null | undefined): string {
  if (n == null) return "";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
}

export function formatPercent(n: number | null | undefined): string {
  if (n == null) return "";
  return `${n.toFixed(1)}%`;
}
