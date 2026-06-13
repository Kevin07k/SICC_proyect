import { COOKIE_UUID } from "@/lib/constants";

export function getUuidFromDocument(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${COOKIE_UUID}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

export function setUuidCookie(uuid: string): void {
  document.cookie = `${COOKIE_UUID}=${encodeURIComponent(uuid)}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;
}

export function clearUuidCookie(): void {
  document.cookie = `${COOKIE_UUID}=; path=/; max-age=0`;
}
