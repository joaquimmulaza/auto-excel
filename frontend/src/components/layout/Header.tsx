"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { UserSwitcher } from "./UserSwitcher";
import { useAuth } from "@/context/AuthContext";
import { Layers, ShieldCheck, Bell, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Header() {
  const pathname = usePathname();
  const { user } = useAuth();

  const isNavActive = (path: string) => {
    if (path === "/" && pathname === "/") return true;
    if (path !== "/" && pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-surface shadow-[0_1px_2px_0_rgba(0,0,0,0.02)]">
      <div className="flex h-14 items-center justify-between px-6">
        {/* Left: Brand Identity */}
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="flex h-7 w-7 items-center justify-center rounded bg-brand text-white font-bold text-xs tracking-wider shadow-sm transition-transform group-hover:scale-105">
              CCM
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold tracking-tight text-ink leading-none">
                Cotarco Commercial Manager
              </span>
              <span className="text-[10px] text-slateSecondary font-medium leading-tight">
                Gestão de Preços & Stock • v1.0
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 pl-4 border-l border-border/80">
            <Link
              href="/"
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-colors ${
                isNavActive("/") && pathname === "/"
                  ? "bg-brand-subtle text-brand"
                  : "text-slateSecondary hover:text-ink hover:bg-canvas"
              }`}
            >
              Dashboard
            </Link>
            <Link
              href="/jobs/new"
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-colors ${
                isNavActive("/jobs/new")
                  ? "bg-brand-subtle text-brand"
                  : "text-slateSecondary hover:text-ink hover:bg-canvas"
              }`}
            >
              Novo Processamento
            </Link>
          </nav>
        </div>

        {/* Right: Engine Status, UserSwitcher, Actions & Profile */}
        <div className="flex items-center gap-3">
          {/* Price Guard Status Indicator */}
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded bg-canvas border border-border text-[11px] text-slateSecondary">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
            <span className="font-mono">Price Guard: Ativo</span>
          </div>

          {/* Role Switcher */}
          <UserSwitcher />

          {/* New Job CTA */}
          <Link href="/jobs/new">
            <Button size="sm" className="hidden sm:inline-flex gap-1.5 font-bold">
              <PlusCircle className="h-3.5 w-3.5" />
              Novo Job
            </Button>
          </Link>

          {/* User Profile Tag */}
          <div className="flex items-center gap-2 pl-2 border-l border-border">
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-canvas border border-border text-xs font-bold text-slateSecondary">
              {user.name.charAt(0)}
            </div>
            <div className="hidden xl:flex flex-col text-left">
              <span className="text-xs font-semibold leading-none text-ink">
                {user.name}
              </span>
              <span className="text-[10px] text-slateSecondary font-medium">
                {user.role === "OPERADOR" ? "Operador de Sistemas" : "Gestor Comercial"}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
