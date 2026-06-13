"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  AlertTriangle,
  Server,
  Users,
  RefreshCw,
  LogOut,
  Shield,
  BarChart3,
  Tags,
} from "lucide-react";
import { useAuth } from "@/lib/auth/AuthContext";
import {
  canSync,
  canViewActivos,
  canViewIncidentes,
  canViewReportes,
  canViewUsuarios,
  canManageTiposIncidente,
} from "@/lib/auth/permissions";
import { SEDE_LABELS } from "@/lib/constants";
import { DEV_SWITCHER_ENABLED } from "@/lib/dev/test-users";
import { cn } from "@/lib/utils";
import { AppShellSkeleton } from "@/components/layout/AppShellSkeleton";
import { DevUserSwitcher } from "@/components/layout/DevUserSwitcher";
import { ClientOnly } from "@/components/shared/ClientOnly";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard, check: () => true },
  {
    href: "/incidentes",
    label: "Incidentes",
    icon: AlertTriangle,
    check: canViewIncidentes,
  },
  { href: "/activos", label: "Activos", icon: Server, check: canViewActivos },
  { href: "/usuarios", label: "Usuarios", icon: Users, check: canViewUsuarios },
  {
    href: "/reportes",
    label: "Reportes globales",
    icon: BarChart3,
    check: canViewReportes,
  },
  { href: "/admin/sync", label: "Sincronización", icon: RefreshCw, check: canSync },
  {
    href: "/admin/tipos-incidente",
    label: "Tipos de incidente",
    icon: Tags,
    check: canManageTiposIncidente,
  },
];

function AppShellInner({
  title,
  actions,
  children,
}: {
  title: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const filteredNav = navItems.filter((item) => item.check(user));

  return (
    <div className="flex min-h-screen bg-slate-950">
      <aside className="flex w-64 flex-col justify-between border-r border-slate-800 bg-slate-900/90 p-4 shadow-xl">
        <div>
          <div className="mb-8 flex items-center gap-2 px-2">
            <Shield className="h-8 w-8 text-blue-500" />
            <div>
              <h1 className="text-lg font-bold text-slate-100">SICC</h1>
              <p className="text-xs text-slate-500">Ciberseguridad</p>
            </div>
          </div>
          <nav className="space-y-1">
            {filteredNav.map(({ href, label, icon: Icon }) => {
              const active = pathname === href || (href !== "/" && pathname.startsWith(href));
              return (
                <Link
                  key={href}
                  href={href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    active
                      ? "bg-blue-950/60 text-blue-300"
                      : "text-slate-400 hover:bg-slate-800 hover:text-slate-200",
                  )}
                >
                  <Icon className="h-5 w-5" />
                  {label}
                </Link>
              );
            })}
          </nav>
          {DEV_SWITCHER_ENABLED && <DevUserSwitcher />}
        </div>
        <div className="space-y-3 border-t border-slate-800 pt-4">
          {user && (
            <div className="rounded-lg bg-slate-800/60 px-3 py-2">
              <p className="truncate text-sm font-medium text-slate-200">
                {user.nombre_completo}
              </p>
              <div className="mt-1 flex flex-wrap gap-1">
                <Badge variant="muted">{user.rol_nombre}</Badge>
                <Badge variant="default">
                  {SEDE_LABELS[user.id_sede] ?? `Sede ${user.id_sede}`}
                </Badge>
              </div>
            </div>
          )}
          <Button variant="destructive" className="w-full" size="sm" onClick={logout}>
            <LogOut className="h-4 w-4" />
            Cerrar sesión
          </Button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto p-8">
        <header className="mb-8 flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/60 px-6 py-5 shadow-md">
          <h2 className="text-2xl font-bold text-slate-100">{title}</h2>
          {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
        </header>
        <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 shadow-md">
          {children}
        </section>
      </main>
    </div>
  );
}

export function AppShell(props: {
  title: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <ClientOnly fallback={<AppShellSkeleton title={props.title} />}>
      <AppShellInner {...props} />
    </ClientOnly>
  );
}
