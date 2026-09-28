import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
import { Header } from "@/components/layout/Header";

export const metadata: Metadata = {
  title: "Cotarco Commercial Manager | Gestão de Tabelas",
  description:
    "Plataforma web interna para recepção, validação, comparação e auditoria de tabelas comerciais de preços e stock.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt" suppressHydrationWarning className="h-full bg-canvas text-ink antialiased">
      <body suppressHydrationWarning className="min-h-full flex flex-col font-sans">
        <Providers>
          <Header />
          <main className="flex-1 pb-16">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
