export interface Usuario {
  uuid: string;
  email: string;
  nombre_completo: string;
  id_sede: number;
  id_rol: number;
  activo: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface UsuarioCreate {
  email: string;
  password: string;
  nombre_completo: string;
  id_rol: number;
  id_sede?: number;
}

export interface UsuarioUpdate {
  email?: string;
  password?: string;
  nombre_completo?: string;
  id_rol?: number;
  activo?: boolean;
}
