import { api } from "@/lib/api/client";
import type { BitacoraCreate, BitacoraEntry } from "@/types/bitacora";

export function listBitacora(incidenteUuid: string): Promise<BitacoraEntry[]> {
  return api<BitacoraEntry[]>(`/incidentes/${incidenteUuid}/bitacora`);
}

export function createBitacora(incidenteUuid: string, body: BitacoraCreate): Promise<BitacoraEntry> {
  return api<BitacoraEntry>(`/incidentes/${incidenteUuid}/bitacora`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
