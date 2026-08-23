"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { useHeartbeat } from "@/hooks/useHeartbeat";

function HeartbeatHandler() {
  useHeartbeat();
  return null;
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        retry: (failureCount, error: any) => {
          if (error.response?.status === 404) {
            return false;
          }
          return failureCount < 3;
        },
      },
    },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      <HeartbeatHandler />
      {children}
    </QueryClientProvider>
  );
}
