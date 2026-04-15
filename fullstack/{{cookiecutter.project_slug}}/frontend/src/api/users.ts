{% if cookiecutter.add_frontend == "y" and cookiecutter.add_strawberry == "n" %}
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { authenticatedFetch } from "../query-client";

// Types - these would typically be shared from the backend or generated
interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
}

interface UsersResponse {
  data: User[];
  count: number;
}

/**
 * Example: Fetch current user
 */
export function useCurrentUser() {
  return useQuery({
    queryKey: ["currentUser"],
    queryFn: async () => {
      const response = await authenticatedFetch("/api/v1/users/me");
      if (!response.ok) {
        throw new Error("Failed to fetch current user");
      }
      return response.json() as Promise<User>;
    },
  });
}

/**
 * Example: Fetch all users with pagination
 */
export function useUsers(skip = 0, limit = 100) {
  return useQuery({
    queryKey: ["users", skip, limit],
    queryFn: async () => {
      const response = await authenticatedFetch(
        `/api/v1/users/?skip=${skip}&limit=${limit}`
      );
      if (!response.ok) {
        throw new Error("Failed to fetch users");
      }
      return response.json() as Promise<UsersResponse>;
    },
  });
}

/**
 * Example: Update user mutation
 */
export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      userId,
      data,
    }: {
      userId: string;
      data: Partial<User>;
    }) => {
      const response = await authenticatedFetch(`/api/v1/users/${userId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error("Failed to update user");
      }
      return response.json() as Promise<User>;
    },
    onSuccess: () => {
      // Invalidate and refetch users queries
      queryClient.invalidateQueries({ queryKey: ["users"] });
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
    },
  });
}
{% endif %}
