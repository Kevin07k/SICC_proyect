import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE_UUID } from "@/lib/constants";

const PUBLIC_PATHS = ["/login"];
const DEV_PATH = "/dev/switch";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const uuid = request.cookies.get(COOKIE_UUID)?.value;

  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    if (uuid) {
      return NextResponse.redirect(new URL("/", request.url));
    }
    return NextResponse.next();
  }

  if (pathname.startsWith(DEV_PATH)) {
    const enabled = process.env.NEXT_PUBLIC_ENABLE_DEV_SWITCHER === "true";
    if (!enabled) {
      return NextResponse.redirect(new URL("/login", request.url));
    }
    return NextResponse.next();
  }

  if (!uuid) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)"],
};
