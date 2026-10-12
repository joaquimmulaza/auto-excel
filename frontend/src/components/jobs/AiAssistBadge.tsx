"use client";

import React from "react";
import { Sparkles } from "lucide-react";

interface AiAssistBadgeProps {
  fallbackUsed?: boolean;
  className?: string;
}

/** Badge obrigatório para conteúdo assistivo (nunca decision-grade). */
export function AiAssistBadge({
  fallbackUsed = false,
  className = "",
}: AiAssistBadgeProps) {
  if (fallbackUsed) {
    return (
      <span
        className={`inline-flex items-center gap-1 text-[10px] font-semibold text-slateSecondary bg-canvas border border-border rounded px-1.5 py-0.5 ${className}`}
      >
        Análise local · IA indisponível
      </span>
    );
  }
  return (
    <span
      className={`inline-flex items-center gap-1 text-[10px] font-semibold text-brand bg-brand-subtle/40 border border-brand/30 rounded px-1.5 py-0.5 ${className}`}
    >
      <Sparkles className="size-3" aria-hidden="true" />
      Assistido por IA
    </span>
  );
}
