#!/usr/bin/env node
/**
 * Renders the React app for the given URL. Called by Flask for SSR.
 * Usage: node ssr-render.mjs [path]
 * Env: API_BASE - base URL for API (e.g. http://localhost:3001)
 * Outputs: JSON with { html, dehydratedState } to stdout
 */
const path = process.argv[2] || "/";

async function run() {
  const { render } = await import("../dist/entry-server.js");
  const { html, dehydratedState } = await render(path);
  process.stdout.write(
    JSON.stringify({
      html,
      dehydratedState: dehydratedState,
    }),
  );
}

run().catch((err) => {
  console.error("SSR render failed:", err);
  process.exit(1);
});
