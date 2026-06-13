"use client";

import { useEffect, useState, type ReactNode } from "react";

/**
 * Renderiza hijos solo en el cliente tras el mount.
 * Evita hydration mismatch con extensiones (Dark Reader, Trancy, etc.)
 * que modifican el DOM antes de que React hidrate.
 */
export function ClientOnly({
  children,
  fallback = null,
}: {
  children: ReactNode;
  fallback?: ReactNode;
}) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return fallback;
  return children;
}
