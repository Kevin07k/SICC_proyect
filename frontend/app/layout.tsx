import type { Metadata } from "next";
import { AuthProvider } from "@/lib/auth/AuthContext";
import { ToasterProvider } from "@/components/ui/toaster";
import "./globals.css";

export const metadata: Metadata = {
  title: "SICC — Sistema Integrado de Ciberseguridad",
  description: "Gestión de incidentes y activos multi-sede",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <ToasterProvider>
          <AuthProvider>{children}</AuthProvider>
        </ToasterProvider>
      </body>
    </html>
  );
}
