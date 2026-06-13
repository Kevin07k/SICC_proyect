import { api, apiPublic } from "@/lib/api/client";
import type { CurrentUser, LoginRequest, LoginResponse } from "@/types/auth";

export async function login(body: LoginRequest): Promise<LoginResponse> {
  return apiPublic<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function getMe(uuid?: string): Promise<CurrentUser> {
  return api<CurrentUser>("/auth/me", { uuid });
}

export async function healthCheck(): Promise<{ status: string }> {
  return apiPublic("/health");
}
