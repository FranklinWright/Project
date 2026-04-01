import type { DehydratedState } from "@tanstack/react-query";
import {
  HydrationBoundary,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import { StrictMode, Suspense } from "react";
import { createRoot, hydrateRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.tsx";

declare global {
  interface Window {
    __REACT_QUERY_STATE__?: DehydratedState;
  }
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
    },
  },
});

const rootElem = document.getElementById("root");
if (!rootElem) {
  throw new Error("Failed to find the root element");
}

const app = (
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <HydrationBoundary state={window.__REACT_QUERY_STATE__}>
        <BrowserRouter>
          <Suspense
            fallback={<div className="container mx-auto p-8">Loading...</div>}
          >
            <App />
          </Suspense>
        </BrowserRouter>
      </HydrationBoundary>
    </QueryClientProvider>
  </StrictMode>
);

const hasServerContent = rootElem.hasChildNodes();

if (import.meta.hot) {
  // With hot module reloading, `import.meta.hot.data` is persisted.
  // biome-ignore lint/suspicious/noAssignInExpressions: intended to persist root across reloads
  const root = (import.meta.hot.data.root ??= createRoot(rootElem));
  root.render(app);
} else if (hasServerContent) {
  hydrateRoot(rootElem, app);
} else {
  createRoot(rootElem).render(app);
}
