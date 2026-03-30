const station = {
  id: 1,
  name: "Austin Station",
  code: "AUS",
  linkedRegion: {
    id: 1,
    name: "Texas",
    code: "TX",
  },
  linkedRoutes: [
    {
      id: 1,
      name: "Texas Eagle",
    },
  ],
};

const region = {
  id: 1,
  name: "Texas",
  code: "TX",
  linkedStations: [station],
  linkedRoutes: [
    {
      id: 1,
      name: "Texas Eagle",
    },
  ],
};

const route = {
  id: 1,
  name: "Texas Eagle",
  linkedStations: [station],
  linkedRegions: [region],
};

const port = Number(Bun.env.MOCK_API_PORT ?? "3000");
const baseUrl = `http://127.0.0.1:${port}`;

const pagination = {
  totalItems: 1,
  totalPages: 1,
  currentPage: 1,
  pageSize: 10,
  hasNextPage: false,
  hasPreviousPage: false,
  links: {
    self: `${baseUrl}/api/stations?page=1&pageSize=10`,
    next: null,
    previous: null,
    first: `${baseUrl}/api/stations?page=1&pageSize=10`,
    last: `${baseUrl}/api/stations?page=1&pageSize=10`,
  },
};

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json",
      "cache-control": "no-store",
    },
  });
}

Bun.serve({
  port,
  fetch(req) {
    const { pathname } = new URL(req.url);

    if (pathname === "/api/stations") {
      return json({ data: [station], pagination });
    }

    if (pathname === "/api/stations/1" || pathname === "/api/stations/AUS") {
      return json(station);
    }

    if (pathname === "/api/regions") {
      return json({
        data: [region],
        pagination: {
          ...pagination,
          links: {
            ...pagination.links,
            self: `${baseUrl}/api/regions?page=1&pageSize=10`,
            first: `${baseUrl}/api/regions?page=1&pageSize=10`,
            last: `${baseUrl}/api/regions?page=1&pageSize=10`,
          },
        },
      });
    }

    if (pathname === "/api/regions/1" || pathname === "/api/regions/TX") {
      return json(region);
    }

    if (pathname === "/api/routes") {
      return json({
        data: [route],
        pagination: {
          ...pagination,
          links: {
            ...pagination.links,
            self: `${baseUrl}/api/routes?page=1&pageSize=10`,
            first: `${baseUrl}/api/routes?page=1&pageSize=10`,
            last: `${baseUrl}/api/routes?page=1&pageSize=10`,
          },
        },
      });
    }

    if (
      pathname === "/api/routes/1" ||
      pathname === "/api/routes/texas-eagle"
    ) {
      return json(route);
    }

    return json({ error: "Not found" }, 404);
  },
});

console.log(`Mock API server running at ${baseUrl}`);
