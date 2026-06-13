export interface Sede {
  id_sede: number;
  nombre_sede: string;
  nivel_criticidad: string;
  eliminado: boolean;
}

export interface Estado {
  id_estado: number;
  nombre: string;
  eliminado: boolean;
}

export interface Prioridad {
  id_prioridad: number;
  nivel: string;
  valor_orden: number;
  eliminado: boolean;
}

export interface TipoIncidente {
  id_tipo: number;
  nombre: string;
  descripcion: string | null;
  eliminado: boolean;
}
