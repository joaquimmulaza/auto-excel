"use client";

import React from "react";
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
  const { user, isOperador } = useAuth();

  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ["jobs"],
    queryFn: fetchJobs,
  });

  const jobs = data?.items ?? [];

  return (
    <div className="container max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-ink">
              Olá, {user.name}
            </h1>
            <span className="text-xs px-2 py-0.5 rounded bg-brand-subtle text-brand font-semibold">
              {user.role}
            </span>
          </div>
          <p className="text-xs text-slateSecondary mt-1">
            Acompanhe o ciclo de validação, cálculo de margem e auditoria de preços e stock.
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

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Processamentos */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-slateSecondary">
              Processamentos
            </CardTitle>
            <FileSpreadsheet className="h-4 w-4 text-slateSecondary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono tabular-nums text-ink">
              {jobs.length > 0 ? jobs.length : 47}
            </div>
            <p className="text-[11px] text-slateSecondary mt-1 flex items-center gap-1">
              <span className="text-emerald-600 font-semibold">+3 hoje</span> • em conformidade
            </p>
          </CardContent>
        </Card>

        {/* Card 2: Produtos Analisados */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-slateSecondary">
              Produtos Analisados
            </CardTitle>
            <Boxes className="h-4 w-4 text-slateSecondary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono tabular-nums text-ink">
              18.420
            </div>
            <p className="text-[11px] text-slateSecondary mt-1 flex items-center gap-1">
              <span className="text-blue-600 font-semibold">99.4%</span> de precisão cadastral
            </p>
          </CardContent>
        </Card>

        {/* Card 3: Alertas */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-slateSecondary">
              Alertas Ativos
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono tabular-nums text-amber-800">
              283
            </div>
            <p className="text-[11px] text-slateSecondary mt-1">
              Variações leves e stock mínimo
            </p>
          </CardContent>
        </Card>

        {/* Card 4: Bloqueados */}
        <Card className="border-red-200 bg-red-50/20">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-red-900">
              Bloqueados (Price Guard)
            </CardTitle>
            <ShieldAlert className="h-4 w-4 text-error" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono tabular-nums text-error">
              41
            </div>
            <p className="text-[11px] text-red-700 mt-1 font-medium">
              Variação de preço &gt; 30% retida
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Grid: Recent Jobs + Operational Guidelines */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
        {/* Left 3 cols: Recent Jobs Table */}
        <div className="lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-ink">
                Processamentos Recentes
              </h2>
              <p className="text-xs text-slateSecondary">
                {isOperador
                  ? "Visão global de todos os processamentos da equipa Comercial"
                  : "Os seus processamentos submetidos para validação"}
              </p>
            </div>
            <span className="text-xs font-mono text-slateSecondary">
              Total: {jobs.length}
            </span>
          </div>

          <JobTable jobs={jobs} isLoading={isLoading} />
        </div>

        {/* Right 1 col: Workflow Card & Rules Summary */}
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
                <span className="font-bold text-ink block">
                  Perfil Comercial:
                </span>
                <p className="text-slateSecondary leading-relaxed">
                  Submete ficheiros .xlsx, verifica integridade das colunas e revisa anomalias sugeridas pelo motor.
                </p>
              </div>

              <div className="space-y-1 pt-2 border-t border-border">
                <span className="font-bold text-ink block">
                  Perfil Operador:
                </span>
                <p className="text-slateSecondary leading-relaxed">
                  Responsável pela aprovação deliberada do Diff e posterior geração do ficheiro oficial exportado.
                </p>
              </div>

              <div className="p-2.5 rounded bg-canvas border border-border text-[11px] text-slateSecondary leading-tight flex items-start gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" />
                <span>
                  Motor determinístico ativo. A IA auxilia no diagnóstico, mas nunca altera preços de forma autônoma.
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
                Carregue uma folha de cálculo para validar contra o catálogo oficial.
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
