"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { TEST_USERS } from "@/lib/dev/test-users";
import { useAuth } from "@/lib/auth/AuthContext";
import { Button } from "@/components/ui/button";

/** Accesos rápidos en login cuando NEXT_PUBLIC_ENABLE_DEV_SWITCHER=true */
export function DevQuickLogin() {
  const router = useRouter();
  const { switchUser } = useAuth();
  const [loadingUuid, setLoadingUuid] = useState<string | null>(null);

  const enterAs = async (uuid: string) => {
    setLoadingUuid(uuid);
    try {
      await switchUser(uuid);
      router.push("/");
    } finally {
      setLoadingUuid(null);
    }
  };

  return (
    <div className="mt-6 space-y-2 rounded-lg border border-amber-600/30 bg-amber-950/20 p-3">
      <p className="text-center text-xs font-semibold uppercase tracking-wide text-amber-400">
        Acceso rápido por sede
      </p>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {TEST_USERS.map((u) => (
          <Button
            key={u.uuid}
            type="button"
            variant="secondary"
            size="sm"
            className="h-auto flex-col py-2 text-left text-xs"
            disabled={loadingUuid !== null}
            onClick={() => void enterAs(u.uuid)}
          >
            <span className="font-medium text-slate-200">{u.sede}</span>
            <span className="text-slate-500">{u.rol}</span>
          </Button>
        ))}
      </div>
    </div>
  );
}
