"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { UserSwitcher } from "./UserSwitcher";
import { useAuth } from "@/context/AuthContext";
import { ShieldCheck, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Header() {
  const pathname = usePathname();
  const { user, canApprove, isAdmin } = useAuth();

  if (pathname === "/login") {
    return (
      <header className="sticky top-0 z-40 w-full border-b border-border bg-surface">
        <div className="flex h-14 items-center px-6">
          <Image
            src="/cotarco-logo.png"
            alt="Cotarco"
            width={104}
            height={32}
            className="h-8 w-auto object-contain"
            priority
            unoptimized
          />
        </div>
      </header>
    );
  }

  const isNavActive = (path: string) => {
    if (path === "/") return pathname === "/";
    return Boolean(pathname?.startsWith(path));
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-surface shadow-[0_1px_2px_0_rgba(0,0,0,0.02)]">
      <div className="flex h-14 items-center justify-between px-6">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="flex items-center transition-transform group-hover:scale-[1.02]">
              <Image
                src="/cotarco-logo.png"
                alt="Cotarco"
                width={104}
                height={32}
                className="h-8 w-auto object-contain"
                priority
                unoptimized
              />
            </div>
            <div className="h-6 w-[1px] bg-border hidden sm:block" />
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="text-sm font-bold tracking-tight text-ink leading-none">
                  Commercial Manager
                </span>
                <span className="text-[10px] font-semibold text-brand bg-brand-subtle px-1.5 py-0.5 rounded leading-none">
                  MVP
                </span>
              </div>
              <span className="text-[10px] text-slateSecondary font-medium leading-tight mt-0.5">
                Gestão de Preços & Stock • v1.0
              </span>
            </div>
          </Link>

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
            {canApprove && (
              <Link
                href="/exceptions"
                className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-colors ${
                  isNavActive("/exceptions")
                    ? "bg-brand-subtle text-brand"
                    : "text-slateSecondary hover:text-ink hover:bg-canvas"
                }`}
              >
                Exceções
              </Link>
            )}
            {isAdmin && (
              <Link
                href="/profiles"
                className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-colors ${
                  isNavActive("/profiles")
                    ? "bg-brand-subtle text-brand"
                    : "text-slateSecondary hover:text-ink hover:bg-canvas"
                }`}
              >
                Perfis
              </Link>
            )}
          </nav>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded bg-canvas border border-border text-[11px] text-slateSecondary">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
            <span className="font-mono">Price Guard: Ativo</span>
          </div>

          <UserSwitcher />

          <Link href="/jobs/new">
            <Button size="sm" className="hidden sm:inline-flex gap-1.5 font-bold">
              <PlusCircle className="h-3.5 w-3.5" />
              Novo Job
            </Button>
          </Link>

          {user && (
            <div className="flex items-center gap-2 pl-2 border-l border-border">
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-canvas border border-border text-xs font-bold text-slateSecondary">
                {user.name.charAt(0)}
              </div>
              <div className="hidden xl:flex flex-col text-left">
                <span className="text-xs font-semibold leading-none text-ink">
                  {user.name}
                </span>
                <span className="text-[10px] text-slateSecondary font-medium">
                  {user.role}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
