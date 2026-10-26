import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes fresh cache
      gcTime: 1000 * 60 * 15,    // 15 minutes before garbage collecting
      refetchOnWindowFocus: false,
      retry: 1
    }
  }
});
