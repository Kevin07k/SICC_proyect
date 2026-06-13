export interface SyncManualResponse {
  last_sync: string;
  tablas_procesadas: string[];
  registros_aplicados: number;
}

export interface SyncTableStatus {
  tabla: string;
  pendientes_postgres: number;
  pendientes_mysql: number;
}

export interface SyncStatusResponse {
  last_sync_postgres: string | null;
  last_sync_mysql: string | null;
  effective_last_sync: string | null;
  tablas: SyncTableStatus[];
}
