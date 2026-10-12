"use client";

import React, { useState } from "react";
import { Sparkles, CheckCircle2 } from "lucide-react";
import { suggestColumnsWithAi } from "@/lib/api";
import { AIColumnMapping } from "@/types";
import { AiAssistBadge } from "@/components/jobs/AiAssistBadge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const DEFAULT_EXPECTED = ["REF", "PRECO", "STOCK"];

interface ColumnMappingAssistProps {
  jobId: string;
  expectedColumns?: string[];
}

/**
 * Sugestões de mapeamento via API backend (Gemini no servidor).
 * Nunca aplica mapeamento sem confirmação humana explícita.
 */
export function ColumnMappingAssist({
  jobId,
  expectedColumns = DEFAULT_EXPECTED,
}: ColumnMappingAssistProps) {
  const [detectedRaw, setDetectedRaw] = useState("Ref Produto, Preco Final, Qtd");
  const [loading, setLoading] = useState(false);
  const [mapping, setMapping] = useState<AIColumnMapping | null>(null);
  const [fallbackUsed, setFallbackUsed] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const parseColumns = (raw: string) =>
    raw
      .split(/[,;\n]/)
      .map((c) => c.trim())
      .filter(Boolean)
      .slice(0, 50);

  const handleSuggest = async () => {
    const detected = parseColumns(detectedRaw);
    if (detected.length === 0) {
      setStatusMsg("Indique pelo menos uma coluna detetada.");
      return;
    }
    setLoading(true);
    setConfirmed(false);
    setStatusMsg(null);
    const result = await suggestColumnsWithAi(jobId, detected, expectedColumns);
    setMapping(result.data);
    setFallbackUsed(result.fallback_used);
    setLoading(false);
  };

  const handleConfirm = () => {
    if (!mapping) return;
    // Guardrail: só regista confirmação humana localmente — o engine
    // determinístico continua a autoridade; não há auto-apply no domínio.
    setConfirmed(true);
    setStatusMsg(
      "Mapeamento confirmado para revisão. O motor determinístico valida antes de processar."
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm flex items-center gap-1.5 text-balance">
          <Sparkles className="size-4 text-brand" aria-hidden="true" />
          Sugestão de mapeamento de colunas
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-xs">
        <p className="text-pretty text-slateSecondary">
          Assistência apenas. Confirme manualmente antes de qualquer uso — zero
          auto-apply.
        </p>
        <label className="block space-y-1.5" htmlFor="detected-columns">
          <span className="font-semibold text-ink">
            Colunas detetadas (separadas por vírgula)
          </span>
          <Input
            id="detected-columns"
            value={detectedRaw}
            onChange={(e) => setDetectedRaw(e.target.value)}
            placeholder="Ex: Ref Produto, Preco Final, Qtd"
            className="text-xs min-h-10"
          />
        </label>
        <p className="text-slateSecondary">
          Esperadas pelo perfil:{" "}
          <span className="font-mono tabular-nums">{expectedColumns.join(", ")}</span>
        </p>
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="gap-1.5 min-h-10"
            onClick={handleSuggest}
            disabled={loading}
            aria-busy={loading}
          >
            <Sparkles className="size-3.5 text-brand" aria-hidden="true" />
            {loading ? "A sugerir…" : "Pedir sugestão"}
          </Button>
          <Button
            type="button"
            size="sm"
            className="gap-1.5 min-h-10"
            onClick={handleConfirm}
            disabled={!mapping || confirmed}
          >
            <CheckCircle2 className="size-3.5" aria-hidden="true" />
            Confirmar mapeamento
          </Button>
        </div>
        {statusMsg && (
          <p className="text-pretty text-ink" role="status" aria-live="polite">
            {statusMsg}
          </p>
        )}
        {mapping && (
          <div className="space-y-2 rounded border border-border bg-canvas p-3">
            <div className="flex items-center justify-between gap-2">
              <span className="font-semibold text-ink">Sugestões</span>
              <AiAssistBadge fallbackUsed={fallbackUsed} />
            </div>
            <ul className="space-y-2">
              {mapping.suggestions.map((s) => (
                <li
                  key={s.detected_column}
                  className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 border-b border-border pb-2"
                >
                  <span className="font-mono text-ink">{s.detected_column}</span>
                  <span className="text-slateSecondary">
                    →{" "}
                    <strong className="text-ink font-mono">
                      {s.suggested_mapping || "—"}
                    </strong>{" "}
                    <span className="tabular-nums">({s.confidence})</span>
                  </span>
                </li>
              ))}
            </ul>
            <p className="text-pretty text-slateSecondary italic">
              {mapping.disclaimer}
            </p>
            {confirmed && (
              <p className="text-emerald-800 font-semibold flex items-center gap-1.5">
                <CheckCircle2 className="size-3.5" aria-hidden="true" />
                Confirmado por humano
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
