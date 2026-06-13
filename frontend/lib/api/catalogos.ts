import { api } from "@/lib/api/client";
import type { Estado, Prioridad, Sede, TipoIncidente } from "@/types/catalogos";

export function listSedes(): Promise<Sede[]> {
  return api<Sede[]>("/catalogos/sedes");
}

export function listEstados(): Promise<Estado[]> {
  return api<Estado[]>("/catalogos/estados");
}

export function listPrioridades(): Promise<Prioridad[]> {
  return api<Prioridad[]>("/catalogos/prioridades");
}

export function listTiposIncidente(): Promise<TipoIncidente[]> {
  return api<TipoIncidente[]>("/catalogos/tipos-incidente");
}

export function listTiposIncidenteGestion(): Promise<TipoIncidente[]> {
  return api<TipoIncidente[]>("/catalogos/tipos-incidente/gestion");
}

export function createTipoIncidente(body: {
  nombre: string;
  descripcion?: string | null;
}): Promise<TipoIncidente> {
  return api<TipoIncidente>("/catalogos/tipos-incidente", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateTipoIncidente(
  id: number,
  body: { nombre?: string; descripcion?: string | null },
): Promise<TipoIncidente> {
  return api<TipoIncidente>(`/catalogos/tipos-incidente/${id}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function deleteTipoIncidente(id: number): Promise<void> {
  return api<void>(`/catalogos/tipos-incidente/${id}`, { method: "DELETE" });
}
