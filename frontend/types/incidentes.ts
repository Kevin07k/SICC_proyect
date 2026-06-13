export interface IncidenteActivoVinculo {
  uuid: string;
  id_incidente: string;
  id_activo: string;
  notas: string | null;
  tipo_activo_registrado: string | null;
  sede_registrada: string | null;
  hostname_registrado: string | null;
  created_at: string | null;
  updated_at: string | null;
  hostname_actual: string | null;
  activo_eliminado: boolean | null;
}

export interface Incidente {
  uuid: string;
  titulo: string;
  descripcion: string | null;
  id_tipo: number;
  id_prioridad: number;
  id_estado: number;
  id_usuario_asignado: string;
  id_sede: number;
  fecha_cierre: string | null;
  eliminado: boolean;
  created_at: string | null;
  updated_at: string | null;
  tipo_nombre: string | null;
  prioridad_nivel: string | null;
  estado_nombre: string | null;
  activos_vinculados?: IncidenteActivoVinculo[];
}

export interface IncidenteCreate {
  titulo: string;
  descripcion?: string | null;
  id_tipo: number;
  id_prioridad: number;
  id_estado: number;
  id_usuario_asignado?: string | null;
  activos?: string[];
}

export interface IncidenteUpdate {
  titulo?: string;
  descripcion?: string | null;
  id_tipo?: number;
  id_prioridad?: number;
  id_estado?: number;
  id_usuario_asignado?: string | null;
  fecha_cierre?: string | null;
  eliminado?: boolean;
}

export interface IncidenteActivoLinkRequest {
  id_activo: string;
  notas?: string | null;
}
