const API_BASE =
  "https://gitlab.com/api/v4/projects/" +
  encodeURIComponent("rail-reach/cs373-group-53380-01");

/**
 * Helper to fetch and count paginated API resources.
 */
async function fetchPaginatedCount(
  url: URL | string,
  perPage: number = 100,
): Promise<number> {
  const paginatedUrl = new URL(url);
  paginatedUrl.searchParams.set("per_page", String(perPage));
  let total = 0;
  let page = 0;
  while (true) {
    const res = await fetch(paginatedUrl);
    const items = await res.json();
    if (!Array.isArray(items)) return total;
    total += items.length;
    if (items.length < perPage) break;
    paginatedUrl.searchParams.set("page", String(++page));
  }
  return total;
}

export function fetchMemberCommits(author: string): Promise<number> {
  const url = new URL(`${API_BASE}/repository/commits`);
  url.searchParams.set("author", author);
  return fetchPaginatedCount(url);
}

export function fetchMemberIssues(author: string): Promise<number> {
  const url = new URL(`${API_BASE}/issues`);
  url.searchParams.set("author_username", author);
  return fetchPaginatedCount(url);
}
