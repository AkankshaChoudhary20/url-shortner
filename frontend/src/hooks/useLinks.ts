import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import type { CreateLinkInput, Link, LinkAnalytics, LinkListResponse } from "../types/link";

const LINKS_QUERY_KEY = ["links"] as const;

export function useLinks(page: number, pageSize = 20) {
  return useQuery({
    queryKey: [...LINKS_QUERY_KEY, page, pageSize],
    queryFn: () =>
      apiClient.get<LinkListResponse>(`/api/v1/links?page=${page}&page_size=${pageSize}`),
  });
}

export function useCreateLink() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateLinkInput) => apiClient.post<Link>("/api/v1/links", input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: LINKS_QUERY_KEY });
    },
  });
}

export function useLinkAnalytics(shortCode: string | null) {
  return useQuery({
    queryKey: ["link-analytics", shortCode],
    queryFn: () => apiClient.get<LinkAnalytics>(`/api/v1/links/${shortCode}/analytics`),
    enabled: shortCode !== null,
  });
}
