import { api } from "@/lib/api/client";
import type {
  Incidente,
  IncidenteActivoLinkRequest,
  IncidenteActivoVinculo,
  IncidenteCreate,
  IncidenteUpdate,
} from "@/types/incidentes";

export function listIncidentes(): Promise<Incidente[]> {
  return api<Incidente[]>("/incidentes");
}

export function getIncidente(uuid: string): Promise<Incidente> {
  return api<Incidente>(`/incidentes/${uuid}`);
}

export function createIncidente(body: IncidenteCreate): Promise<Incidente> {
  return api<Incidente>("/incidentes", { method: "POST", body: JSON.stringify(body) });
}

export function updateIncidente(uuid: string, body: IncidenteUpdate): Promise<Incidente> {
  return api<Incidente>(`/incidentes/${uuid}`, { method: "PATCH", body: JSON.stringify(body) });
}

export function listActivosIncidente(incidenteUuid: string): Promise<IncidenteActivoVinculo[]> {
  return api<IncidenteActivoVinculo[]>(`/incidentes/${incidenteUuid}/activos`);
}

export function linkActivoIncidente(
  incidenteUuid: string,
  body: IncidenteActivoLinkRequest,
): Promise<IncidenteActivoVinculo> {
  return api<IncidenteActivoVinculo>(`/incidentes/${incidenteUuid}/activos`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function unlinkActivoIncidente(
  incidenteUuid: string,
  vinculoUuid: string,
): Promise<void> {
  return api<void>(`/incidentes/${incidenteUuid}/activos/${vinculoUuid}`, {
    method: "DELETE",
  });
}
