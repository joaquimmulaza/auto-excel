"use client";

import React from "react";
import { useAuth } from "@/context/AuthContext";
import { UserRole } from "@/types";
import { ShieldAlert, UserCheck } from "lucide-react";

export function UserSwitcher() {
  const { user, setRole } = useAuth();

  return (
    <div className="flex items-center gap-1.5 rounded-md border border-border bg-canvas p-1">
      <span className="text-[11px] font-semibold uppercase text-slateSecondary px-1.5">
        Perfil:
      </span>
      <button
        type="button"
        onClick={() => setRole("COMERCIAL")}
        className={`flex items-center gap-1 rounded px-2.5 py-1 text-xs font-semibold transition-all ${
          user.role === "COMERCIAL"
            ? "bg-surface text-ink shadow-sm border border-border text-brand"
            : "text-slateSecondary hover:text-ink"
        }`}
      >
        <UserCheck className="h-3.5 w-3.5" />
        Comercial
      </button>
      <button
        type="button"
        onClick={() => setRole("OPERADOR")}
        className={`flex items-center gap-1 rounded px-2.5 py-1 text-xs font-semibold transition-all ${
          user.role === "OPERADOR"
            ? "bg-brand text-white shadow-sm font-bold"
            : "text-slateSecondary hover:text-ink"
        }`}
      >
        <ShieldAlert className="h-3.5 w-3.5" />
        Operador
      </button>
    </div>
  );
}
