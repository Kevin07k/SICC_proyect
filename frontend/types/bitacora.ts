export interface BitacoraEntry {
  uuid: string;
  id_incidente: string;
  id_usuario: string;
  comentario: string;
  eliminado: boolean;
  created_at: string | null;
  usuario_nombre: string | null;
}

export interface BitacoraCreate {
  comentario: string;
}
