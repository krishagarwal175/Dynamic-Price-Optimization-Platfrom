/** Typed API client. The only layer that talks to the backend.
 *
 * Every response uses the standard envelope: `{ data, meta }` on success or
 * `{ error, meta }` on failure. `apiGet` unwraps `data` or throws `ApiError`.
 */

const BASE_URL = "/api/v1";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly code: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type QueryValue = string | number | boolean | null | undefined;

function buildQuery(params?: Record<string, QueryValue>): string {
  if (!params) return "";
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      search.append(key, String(value));
    }
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

interface SuccessEnvelope<T> {
  data: T;
}

interface ErrorEnvelope {
  error: { code: string; message: string };
}

export async function apiGet<T>(
  path: string,
  params?: Record<string, QueryValue>,
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}${buildQuery(params)}`, {
      headers: { Accept: "application/json" },
    });
  } catch {
    throw new ApiError("Unable to reach the server.", "NETWORK_ERROR", 0);
  }

  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    const err = (body as ErrorEnvelope | null)?.error;
    throw new ApiError(
      err?.message ?? response.statusText ?? "Request failed.",
      err?.code ?? "UNKNOWN",
      response.status,
    );
  }
  return (body as SuccessEnvelope<T>).data;
}
