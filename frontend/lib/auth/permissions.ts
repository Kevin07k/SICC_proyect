import type { CurrentUser } from "@/types/auth";
import { SEDE_CENTRAL_ID } from "@/lib/constants";

export function isAdmin(user: CurrentUser | null): boolean {
  return user?.rol_nombre === "Administrador";
}

export function hasPermiso(user: CurrentUser | null, codigo: string): boolean {
  if (!user) return false;
  if (isAdmin(user)) return true;
  return user.permisos.includes(codigo);
}

export function canViewIncidentes(user: CurrentUser | null): boolean {
  return hasPermiso(user, "incidentes.ver");
}

export function canManageIncidentes(user: CurrentUser | null): boolean {
  return hasPermiso(user, "incidentes.gestionar");
}

export function canViewActivos(user: CurrentUser | null): boolean {
  return hasPermiso(user, "activos.ver");
}

export function canManageActivos(user: CurrentUser | null): boolean {
  return hasPermiso(user, "activos.gestionar");
}

export function canViewUsuarios(user: CurrentUser | null): boolean {
  return hasPermiso(user, "usuarios.ver");
}

export function canManageUsuarios(user: CurrentUser | null): boolean {
  return hasPermiso(user, "usuarios.gestionar");
}

export function canSync(user: CurrentUser | null): boolean {
  return hasPermiso(user, "sync.ejecutar");
}

export function canViewBitacora(user: CurrentUser | null): boolean {
  return hasPermiso(user, "bitacora.ver");
}

export function canViewDocumentos(user: CurrentUser | null): boolean {
  return (
    hasPermiso(user, "documentos.ver") ||
    hasPermiso(user, "incidentes.ver") ||
    hasPermiso(user, "activos.ver")
  );
}

/** Alta de evidencias / timeline Mongo en incidentes */
export function canManageDocumentosIncidente(user: CurrentUser | null): boolean {
  return (
    hasPermiso(user, "documentos.gestionar") || hasPermiso(user, "incidentes.gestionar")
  );
}

/** Alta de telemetría Mongo en activos */
export function canManageDocumentosActivo(user: CurrentUser | null): boolean {
  return hasPermiso(user, "documentos.gestionar") || hasPermiso(user, "activos.gestionar");
}

export function isSedeCentral(user: CurrentUser | null): boolean {
  return user?.id_sede === SEDE_CENTRAL_ID;
}

export function canViewReportes(user: CurrentUser | null): boolean {
  return isSedeCentral(user) && hasPermiso(user, "reportes.ver");
}

export function canManageTiposIncidente(user: CurrentUser | null): boolean {
  return isSedeCentral(user) && hasPermiso(user, "catalogos.gestionar");
}
