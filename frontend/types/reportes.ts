export interface SedeMetricas {
  id_sede: number;
  nombre_sede: string;
  incidentes_total: number;
  incidentes_abiertos: number;
  activos_total: number;
  activos_activos: number;
  nodo: string;
}

export interface ConteoItem {
  nombre: string;
  cantidad: number;
}

export interface ReporteGlobalPayload {
  sedes: SedeMetricas[];
  incidentes_por_estado: ConteoItem[];
  incidentes_por_prioridad: ConteoItem[];
  totales: Record<string, number>;
}

export interface ReporteGlobalResponse {
  from_cache: boolean;
  generated_at: string;
  expires_at: string;
  ttl_seconds: number;
  duration_ms: number | null;
  payload: ReporteGlobalPayload;
}
