import type { ApiEnvelope } from "@/lib/types";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly details: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiRequest<T>(
  path: string,
  init?: RequestInit,
): Promise<ApiEnvelope<T>> {
  const headers = new Headers(init?.headers);
  if (init?.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`/api/backend/${path.replace(/^\/+/, "")}`, {
    ...init,
    headers,
    credentials: "same-origin",
    cache: "no-store",
  });
  if (response.status === 204) {
    return { data: undefined as T };
  }

  const payload = (await response.json().catch(() => null)) as
    | (ApiEnvelope<T> & { error?: { message?: string } })
    | null;
  if (!response.ok) {
    throw new ApiError(
      payload?.error?.message ?? `API request failed with status ${response.status}.`,
      response.status,
      payload,
    );
  }
  if (!payload || !("data" in payload)) {
    throw new ApiError("The API returned an unexpected response.", response.status, payload);
  }
  return payload;
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return "Something went wrong. Please try again.";
}
