import { getUuidFromDocument } from "@/lib/auth/cookie";

const base = () => process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function parseError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data?.detail === "string") return data.detail;
    if (Array.isArray(data?.detail)) {
      return data.detail.map((d: { msg?: string }) => d.msg ?? JSON.stringify(d)).join(", ");
    }
  } catch {
    /* ignore */
  }
  return res.statusText || `Error ${res.status}`;
}

export interface ApiOptions extends RequestInit {
  auth?: boolean;
  uuid?: string;
}

export async function api<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const { auth = true, uuid, ...init } = options;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };

  if (auth) {
    const userUuid = uuid ?? getUuidFromDocument();
    if (!userUuid) throw new ApiError(401, "No autenticado");
    headers["X-Usuario-UUID"] = userUuid;
  }

  const res = await fetch(`${base()}${path}`, { ...init, headers });

  if (!res.ok) {
    throw new ApiError(res.status, await parseError(res));
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export async function apiPublic<T>(path: string, init?: RequestInit): Promise<T> {
  return api<T>(path, { ...init, auth: false });
}
