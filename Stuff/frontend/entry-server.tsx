import { PassThrough } from "node:stream";
import {
  dehydrate,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import { Suspense } from "react";
import { renderToPipeableStream } from "react-dom/server";
import { StaticRouter } from "react-router-dom";
import App from "./App.tsx";

function collectStream(stream: PassThrough): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    stream.on("data", (chunk: Buffer) => chunks.push(chunk));
    stream.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    stream.on("error", reject);
  });
}

export async function render(url: string): Promise<{
  html: string;
  dehydratedState: ReturnType<typeof dehydrate>;
}> {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60 * 5,
      },
    },
  });

  const app = (
    <QueryClientProvider client={queryClient}>
      <StaticRouter location={url}>
        <Suspense
          fallback={<div className="container mx-auto p-8">Loading...</div>}
        >
          <App />
        </Suspense>
      </StaticRouter>
    </QueryClientProvider>
  );

  const { pipe } = renderToPipeableStream(app, {
    onAllReady() {
      // Stream will finish after this when all suspense resolved
    },
  });

  const passThrough = new PassThrough();
  pipe(passThrough);
  const html = await collectStream(passThrough);
  const dehydratedState = dehydrate(queryClient);

  return { html, dehydratedState };
}
