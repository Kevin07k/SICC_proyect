#!/usr/bin/env node
/**
 * Smoke test: valida contrato API sin Playwright.
 * Uso: npm run smoke  (requiere API en NEXT_PUBLIC_API_URL o localhost:8000)
 */
const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const ADMIN_UUID = "11111111-1111-1111-1111-111111111101";

async function req(path, init = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init.headers },
    ...init,
  });
  const text = await res.text();
  let body;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = text;
  }
  if (!res.ok) {
    throw new Error(`${init.method || "GET"} ${path} → ${res.status}: ${JSON.stringify(body)}`);
  }
  return body;
}

async function main() {
  console.log("Smoke API →", BASE);

  const health = await req("/health");
  console.log("✓ GET /health", health.status);

  const login = await req("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email: "admin@sicc.com", password: "admin123" }),
  });
  const uuid = login.uuid || ADMIN_UUID;
  console.log("✓ POST /auth/login", login.email);

  const headers = { "X-Usuario-UUID": uuid };

  const me = await req("/auth/me", { headers });
  console.log("✓ GET /auth/me", me.rol_nombre);

  const incidentes = await req("/incidentes", { headers });
  console.log("✓ GET /incidentes", Array.isArray(incidentes) ? incidentes.length : 0, "items");

  const activos = await req("/activos", { headers });
  console.log("✓ GET /activos", Array.isArray(activos) ? activos.length : 0, "items");

  const sedes = await req("/catalogos/sedes", { headers });
  console.log("✓ GET /catalogos/sedes", sedes.length, "sedes");

  if (me.permisos?.includes("sync.ejecutar") || me.rol_nombre === "Administrador") {
    const sync = await req("/sync/status", { headers });
    console.log("✓ GET /sync/status", sync.tablas?.length ?? 0, "tablas");
  }

  console.log("\nSmoke OK");
}

main().catch((e) => {
  console.error("Smoke FAILED:", e.message);
  process.exit(1);
});
