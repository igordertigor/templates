{% if cookiecutter.add_frontend == "y" and cookiecutter.add_strawberry == "n" %}
import { QueryClient } from "@tanstack/react-query";
import { userManager } from "./auth/oidc";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

/**
 * Helper to make authenticated API requests with TanStack Query
 * Automatically attaches the access token from Authentik
 */
export async function authenticatedFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const user = await userManager.getUser();
  const headers = new Headers(options.headers);

  if (user?.access_token) {
    headers.set("Authorization", `Bearer ${user.access_token}`);
  }

  return fetch(url, {
    ...options,
    headers,
  });
}
{% endif %}
