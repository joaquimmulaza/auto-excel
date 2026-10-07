"use client";

import React, { useMemo } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { fetchJobs } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { JobTable } from "@/components/jobs/JobTable";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  FileSpreadsheet,
  Boxes,
  AlertTriangle,
  ShieldAlert,
  PlusCircle,
  RefreshCw,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";

export default function DashboardPage() {
  const { user, isOperador, canApprove } = useAuth();

  const { data, isLoading, refetch, isFetching, error } = useQuery({
    queryKey: ["jobs"],
    queryFn: fetchJobs,
  });

  const jobs = useMemo(() => data?.items ?? [], [data?.items]);

  const kpis = useMemo(() => {
    let products = 0;
    let blocked = 0;
    let needsReview = 0;
    for (const j of jobs) {
      products += Number(j.summary?.total ?? 0);
      blocked += Number(j.summary?.blocked ?? 0);
      if (j.status === "READY_FOR_REVIEW" || j.status === "NEEDS_CORRECTION") {
        needsReview += 1;
      }
    }
    return { products, blocked, needsReview };
  }, [jobs]);

  return (
    <div className="container max-w-7xl mx-auto px-4 py-8 space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-ink">
              Olá, {user?.name || "utilizador"}
            </h1>
            <span className="text-xs px-2 py-0.5 rounded bg-brand-subtle text-brand font-semibold">
              {user?.role}
            </span>
          </div>
          <p className="text-xs text-slateSecondary mt-1">
            Acompanhe o ciclo de validação, aprovação e exportação de preços e stock.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isFetching}
            className="gap-1.5 text-xs text-slateSecondary"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isFetching ? "animate-spin" : ""}`} />
            Atualizar
          </Button>
          <Link href="/jobs/new">
            <Button size="sm" className="gap-1.5 font-bold">
              <PlusCircle className="h-4 w-4" />
              Novo Processamento
            </Button>
          </Link>
        </div>
      </div>

      {error && (
        <div className="text-xs text-error border border-red-200 bg-red-50 rounded p-3">
          {(error as Error).message}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-slateSecondary">
              Processamentos
            </CardTitle>
            <FileSpreadsheet className="h-4 w-4 text-slateSecondary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono tabular-nums text-ink">
              {jobs.length}
            </div>
            <p className="text-[11px] text-slateSecondary mt-1">
              Total visível para o seu perfil
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-slateSecondary">
              Produtos Analisados
            </CardTitle>
            <Boxes className="h-4 w-4 text-slateSecondary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono tabular-nums text-ink">
              {kpis.products.toLocaleString("pt-PT")}
            </div>
            <p className="text-[11px] text-slateSecondary mt-1">Soma dos totais dos lotes</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-slateSecondary">
              Em Revisão
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono tabular-nums text-amber-800">
              {kpis.needsReview}
            </div>
            <p className="text-[11px] text-slateSecondary mt-1">
              READY_FOR_REVIEW / NEEDS_CORRECTION
            </p>
          </CardContent>
        </Card>

        <Card className="border-red-200 bg-red-50/20">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-red-900">
              Bloqueados (Price Guard)
            </CardTitle>
            <ShieldAlert className="h-4 w-4 text-error" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono tabular-nums text-error">
              {kpis.blocked}
            </div>
            <p className="text-[11px] text-red-700 mt-1 font-medium">
              {canApprove ? (
                <Link href="/exceptions" className="underline">
                  Ver fila de exceções
                </Link>
              ) : (
                "Itens retidos pelos limiares"
              )}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
        <div className="lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-ink">Processamentos Recentes</h2>
              <p className="text-xs text-slateSecondary">
                {isOperador
                  ? "Visão global de todos os processamentos"
                  : "Os seus processamentos submetidos"}
              </p>
            </div>
            <span className="text-xs font-mono text-slateSecondary">Total: {jobs.length}</span>
          </div>
          <JobTable jobs={jobs} isLoading={isLoading} />
        </div>

        <div className="space-y-4">
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-1.5 text-ink">
                <ShieldCheck className="h-4 w-4 text-brand" />
                Governança Operacional
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3.5 text-xs">
              <div className="space-y-1">
                <span className="font-bold text-ink block">Comercial:</span>
                <p className="text-slateSecondary leading-relaxed">
                  Submete Excel, valida e acompanha o diff sem aprovar exportação.
                </p>
              </div>
              <div className="space-y-1 pt-2 border-t border-border">
                <span className="font-bold text-ink block">Operador:</span>
                <p className="text-slateSecondary leading-relaxed">
                  Aprova o lote e gera OUTPUT + LOG oficiais.
                </p>
              </div>
              <div className="p-2.5 rounded bg-canvas border border-border text-[11px] text-slateSecondary leading-tight flex items-start gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" />
                <span>
                  Motor determinístico ativo. A IA auxilia no diagnóstico, mas nunca altera preços.
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-brand-subtle/40 border-brand/20">
            <CardContent className="p-4 space-y-2">
              <span className="text-xs font-bold text-brand uppercase tracking-wider block">
                Novo Lote?
              </span>
              <p className="text-xs text-ink/80 leading-relaxed">
                Carregue uma folha de cálculo para validar contra o catálogo.
              </p>
              <Link href="/jobs/new" className="inline-block pt-1">
                <Button size="sm" variant="default" className="gap-1 text-xs">
                  Criar Lote
                  <ArrowRight className="h-3 w-3" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
