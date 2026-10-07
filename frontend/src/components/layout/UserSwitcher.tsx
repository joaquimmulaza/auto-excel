"use client";

import React from "react";
import { useAuth } from "@/context/AuthContext";
import { LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";

export function UserSwitcher() {
  const { user, logout } = useAuth();
  if (!user) return null;

  return (
    <div className="flex items-center gap-2">
      <span className="hidden sm:inline text-[11px] font-semibold uppercase text-slateSecondary px-1.5">
        {user.role}
      </span>
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={logout}
        className="gap-1.5 text-xs"
      >
        <LogOut className="h-3.5 w-3.5" />
        Sair
      </Button>
    </div>
  );
}
