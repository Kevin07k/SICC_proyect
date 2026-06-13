"use client";

import { useRouter } from "next/navigation";
import { FlaskConical, Shield } from "lucide-react";
import { TEST_USERS } from "@/lib/dev/test-users";
import { setUuidCookie } from "@/lib/auth/cookie";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";

export default function DevSwitchPage() {
  const router = useRouter();

  const selectUser = (uuid: string) => {
    setUuidCookie(uuid);
    router.push("/");
    router.refresh();
  };

  return (
    <div className="dev-panel-bg flex min-h-screen flex-col items-center justify-center p-6">
      <div className="mb-8 text-center">
        <FlaskConical className="mx-auto mb-3 h-12 w-12 text-amber-500" />
        <h1 className="text-2xl font-bold text-amber-100">Panel de prueba SICC</h1>
        <p className="mt-2 text-slate-400">
          Cambia de usuario sin contraseña. Solo desarrollo.
        </p>
      </div>
      <div className="grid w-full max-w-2xl gap-4 sm:grid-cols-2">
        {TEST_USERS.map((u) => (
          <Card
            key={u.uuid}
            className="cursor-pointer border-amber-800/30 transition hover:border-amber-600/50"
            onClick={() => selectUser(u.uuid)}
          >
            <CardHeader className="pb-2">
              <CardTitle className="text-base text-slate-100">{u.nombre}</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-slate-400">
              <p>{u.email}</p>
              <p className="mt-1">
                <span className="text-amber-400">{u.rol}</span> · {u.sede}
              </p>
              <Button className="mt-4 w-full" size="sm" variant="secondary">
                Entrar como este usuario
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
      <Link
        href="/login"
        className="mt-8 flex items-center gap-2 text-sm text-slate-500 hover:text-slate-300"
      >
        <Shield className="h-4 w-4" />
        Ir al login normal
      </Link>
    </div>
  );
}
