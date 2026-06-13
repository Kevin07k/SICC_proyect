import { api } from "@/lib/api/client";
import type { ReporteGlobalResponse } from "@/types/reportes";

/** Lee el reporte global (usa caché en PG si sigue vigente). */
export function getReporteGlobal(refresh = false): Promise<ReporteGlobalResponse> {
  const q = refresh ? "?refresh=true" : "";
  return api<ReporteGlobalResponse>(`/reportes/global${q}`);
}

/** Fuerza recálculo cross-sede y actualiza la caché. */
export function regenerarReporteGlobal(): Promise<ReporteGlobalResponse> {
  return api<ReporteGlobalResponse>("/reportes/global/regenerar", {
    method: "POST",
  });
}
