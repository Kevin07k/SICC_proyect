"use client";

import { createContext, useCallback, useContext, useState, type ReactNode } from "react";
import {
  Toast,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from "@/components/ui/toast";

interface ToastItem {
  id: string;
  title: string;
  description?: string;
  variant?: "default" | "error";
}

interface ToastContextValue {
  toast: (title: string, description?: string, variant?: "default" | "error") => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToasterProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);

  const toast = useCallback(
    (title: string, description?: string, variant: "default" | "error" = "default") => {
      const id = crypto.randomUUID();
      setItems((prev) => [...prev, { id, title, description, variant }]);
      setTimeout(() => setItems((prev) => prev.filter((t) => t.id !== id)), 4000);
    },
    [],
  );

  return (
    <ToastContext.Provider value={{ toast }}>
      <ToastProvider>
        {children}
        {items.map((item) => (
          <Toast key={item.id} variant={item.variant} open>
            <div className="grid gap-1">
              <ToastTitle>{item.title}</ToastTitle>
              {item.description && <ToastDescription>{item.description}</ToastDescription>}
            </div>
          </Toast>
        ))}
        <ToastViewport />
      </ToastProvider>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast dentro de ToasterProvider");
  return ctx;
}
