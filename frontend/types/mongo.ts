export interface Evidencia {
  id: string;
  incidente_uuid: string;
  tipo: string;
  metadata?: Record<string, unknown> | null;
  iocs?: Array<Record<string, unknown>> | null;
  lineas?: string[] | null;
  autor_uuid: string;
  created_at: string;
  eliminado: boolean;
}

export interface EvidenciaCreate {
  tipo: string;
  metadata?: Record<string, unknown> | null;
  iocs?: Array<Record<string, unknown>> | null;
  lineas?: string[] | null;
}

export interface TimelineEvento {
  id: string;
  incidente_uuid: string;
  tipo_evento: string;
  payload: Record<string, unknown>;
  autor_uuid: string;
  created_at: string;
  eliminado: boolean;
}

export interface TimelineEventoCreate {
  tipo_evento: string;
  payload?: Record<string, unknown>;
}

export interface Telemetria {
  id: string;
  activo_uuid: string;
  tipo_escaneo: string;
  captured_at: string;
  hallazgos?: Array<Record<string, unknown>> | null;
  snapshot?: Record<string, unknown> | null;
  eliminado: boolean;
}

export interface TelemetriaCreate {
  tipo_escaneo: string;
  hallazgos?: Array<Record<string, unknown>> | null;
  snapshot?: Record<string, unknown> | null;
}
