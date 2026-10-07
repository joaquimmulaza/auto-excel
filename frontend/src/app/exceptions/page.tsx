"use client";

import React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { fetchExceptions, explainBlockCode } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertOctagon, ArrowLeft } from "lucide-react";

export default function ExceptionsPage() {
  const { canApprove } = useAuth();
  const { data, isLoading, error } = useQuery({
    queryKey: ["exceptions"],
    queryFn: fetchExceptions,
    enabled: canApprove,
  });

  if (!canApprove) {
    return (
      <div className="container max-w-5xl mx-auto px-4 py-8 text-sm text-slateSecondary">
        Apenas Operador/Admin pode aceder à fila de exceções.
      </div>
    );
  }

  const items = data?.items ?? [];

  return (
    <div className="container max-w-5xl mx-auto px-4 py-8 space-y-6">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs text-slateSecondary hover:text-ink font-semibold"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        Voltar
      </Link>
      <div>
        <h1 className="text-2xl font-bold text-ink flex items-center gap-2">
          <AlertOctagon className="h-6 w-6 text-error" />
          Fila de Exceções
        </h1>
        <p className="text-xs text-slateSecondary mt-1">
          Itens bloqueados ordenados por variação e valor estimado.
        </p>
      </div>

      {error && (
        <p className="text-xs text-error">{(error as Error).message}</p>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">
            {isLoading ? "A carregar…" : `${items.length} exceções`}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {items.length === 0 && !isLoading && (
            <p className="text-xs text-slateSecondary">Nenhuma exceção aberta.</p>
          )}
          {items.map((item) => (
            <div
              key={String(item.item_id)}
              className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border border-border rounded p-3 text-xs"
            >
              <div>
                <div className="font-mono font-bold text-ink">
                  {String(item.reference_normalized)}
                </div>
                <p className="text-slateSecondary mt-0.5">
                  Job #{String(item.job_number)} · {explainBlockCode(String(item.decision_code || ""))}
                  {item.price_variation_pct != null && (
                    <> · {Number(item.price_variation_pct).toFixed(1)}%</>
                  )}
                </p>
              </div>
              <Link href={`/jobs/${item.job_id}`}>
                <Button size="sm" variant="outline">
                  Abrir job
                </Button>
              </Link>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
