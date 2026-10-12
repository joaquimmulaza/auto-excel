"use client";

import React, { useState } from "react";
import { Sparkles } from "lucide-react";
import { summarizeJobWithAi } from "@/lib/api";
import { AIExecutiveSummary } from "@/types";
import { AiAssistBadge } from "@/components/jobs/AiAssistBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface AiJobSummaryCardProps {
  jobId: string;
}

export function AiJobSummaryCard({ jobId }: AiJobSummaryCardProps) {
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<AIExecutiveSummary | null>(null);
  const [fallbackUsed, setFallbackUsed] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    const result = await summarizeJobWithAi(jobId);
    setSummary(result.data);
    setFallbackUsed(result.fallback_used);
    if (!result.data?.headline) {
      setError("Não foi possível gerar o resumo.");
    }
    setLoading(false);
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-3 space-y-0">
        <CardTitle className="text-sm flex items-center gap-1.5 text-balance">
          <Sparkles className="size-4 text-brand" aria-hidden="true" />
          Resumo assistivo
        </CardTitle>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="gap-1.5 text-xs min-h-10"
          onClick={handleGenerate}
          disabled={loading}
          aria-busy={loading}
        >
          <Sparkles className="size-3.5 text-brand" aria-hidden="true" />
          {loading ? "A gerar…" : summary ? "Atualizar resumo" : "Gerar com IA"}
        </Button>
      </CardHeader>
      <CardContent className="space-y-3 text-xs">
        <p className="text-pretty text-slateSecondary">
          Contextualiza os números do motor determinístico. Não altera preços,
          stock nem aprovações.
        </p>
        {error && (
          <p className="text-error" role="alert">
            {error}
          </p>
        )}
        {loading && (
          <div
            className="flex items-center gap-2 text-slateSecondary py-2"
            role="status"
            aria-live="polite"
          >
            <div className="size-4 rounded-full border-2 border-brand border-t-transparent animate-spin" />
            A pedir resumo ao backend…
          </div>
        )}
        {summary && !loading && (
          <div className="space-y-2 rounded border border-brand/20 bg-brand-subtle/20 p-3">
            <div className="flex items-center justify-between gap-2">
              <p className="font-semibold text-ink text-pretty">{summary.headline}</p>
              <AiAssistBadge fallbackUsed={fallbackUsed} />
            </div>
            <ul className="list-disc pl-4 space-y-1 text-ink/90">
              {summary.highlights.map((h) => (
                <li key={h}>{h}</li>
              ))}
            </ul>
            {summary.attention_items?.length > 0 && (
              <div>
                <p className="font-semibold text-ink mb-1">Atenção</p>
                <ul className="list-disc pl-4 space-y-1 text-amber-900">
                  {summary.attention_items.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
            <p className="text-pretty text-slateSecondary border-t border-border pt-2">
              {summary.overall_assessment}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
