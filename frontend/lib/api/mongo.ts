import { api } from "@/lib/api/client";
import type {
  Evidencia,
  EvidenciaCreate,
  Telemetria,
  TelemetriaCreate,
  TimelineEvento,
  TimelineEventoCreate,
} from "@/types/mongo";

export function listEvidencias(incidenteUuid: string): Promise<Evidencia[]> {
  return api<Evidencia[]>(`/incidentes/${incidenteUuid}/evidencias`);
}

export function createEvidencia(
  incidenteUuid: string,
  body: EvidenciaCreate,
): Promise<Evidencia> {
  return api<Evidencia>(`/incidentes/${incidenteUuid}/evidencias`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function listTimeline(incidenteUuid: string): Promise<TimelineEvento[]> {
  return api<TimelineEvento[]>(`/incidentes/${incidenteUuid}/timeline`);
}

export function createTimeline(
  incidenteUuid: string,
  body: TimelineEventoCreate,
): Promise<TimelineEvento> {
  return api<TimelineEvento>(`/incidentes/${incidenteUuid}/timeline`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function listTelemetria(activoUuid: string): Promise<Telemetria[]> {
  return api<Telemetria[]>(`/activos/${activoUuid}/telemetria`);
}

export function createTelemetria(
  activoUuid: string,
  body: TelemetriaCreate,
): Promise<Telemetria> {
  return api<Telemetria>(`/activos/${activoUuid}/telemetria`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
