export interface LoginRequest {
  email: string;
  password: string;
}

export interface CurrentUser {
  uuid: string;
  email: string;
  nombre_completo: string;
  id_sede: number;
  id_rol: number;
  rol_nombre: string;
  permisos: string[];
}

export type LoginResponse = CurrentUser;
