import type { DiscoveryResponse, InstitutionSearchResponse } from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const fallbackMessage = `API request failed with status ${response.status}`;
    let message = fallbackMessage;

    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        message = payload.detail;
      }
    } catch {
      // Keep fallback message when response body is not JSON.
    }

    throw new ApiError(message, response.status);
  }

  return (await response.json()) as T;
}

export async function fetchInstitutions(
  query: string,
  limit = 10,
): Promise<InstitutionSearchResponse> {
  const params = new URLSearchParams({ query, limit: String(limit) });
  const response = await fetch(`${API_BASE_URL}/api/v1/institutions?${params}`);
  return parseResponse<InstitutionSearchResponse>(response);
}

export async function fetchDiscovery(params: {
  topic: string;
  institutionId: string;
  offset?: number;
  limit?: number;
}): Promise<DiscoveryResponse> {
  const query = new URLSearchParams({
    topic: params.topic,
    institution_id: params.institutionId,
    offset: String(params.offset ?? 0),
    limit: String(params.limit ?? 10)
  });

  const response = await fetch(`${API_BASE_URL}/api/v1/discovery?${query}`);
  return parseResponse<DiscoveryResponse>(response);
}
