export interface Activo {
  uuid: string;
  hostname: string;
  direccion_ip: string | null;
  tipo_activo: string | null;
  propietario: string | null;
  id_sede: number;
  eliminado: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface ActivoCreate {
  hostname: string;
  direccion_ip?: string | null;
  tipo_activo?: string | null;
  propietario?: string | null;
}

export interface ActivoUpdate {
  hostname?: string;
  direccion_ip?: string | null;
  tipo_activo?: string | null;
  propietario?: string | null;
  eliminado?: boolean;
}

export interface ActivoTransferirRequest {
  sede_destino_id: number;
  motivo: string;
}

export interface ActivoTransferirResponse {
  uuid: string;
  sede_origen_id: number;
  sede_destino_id: number;
  nodo_origen: string;
  nodo_destino: string;
  motivo: string;
}
