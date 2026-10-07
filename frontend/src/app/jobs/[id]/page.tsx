"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  fetchJob,
  fetchJobSummary,
  fetchJobItems,
  fetchJobIssues,
  approveJob,
  rejectJob,
  processJob,
  listJobFiles,
  downloadJobFile,
  fetchReceipt,
  fetchPriceHistory,
  explainBlockCode,
} from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { DiffViewer } from "@/components/jobs/DiffViewer";
import { ValidationIssueList } from "@/components/jobs/ValidationIssueList";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatDate, formatNumber } from "@/lib/utils";
import {
  ArrowLeft,
  CheckCircle2,
  AlertOctagon,
  ShieldCheck,
  ShieldAlert,
  Clock,
  FileCheck2,
  Download,
  Play,
  XCircle,
  Receipt,
} from "lucide-react";

export default function JobDetailPage() {
  const params = useParams();
  const queryClient = useQueryClient();
  const jobId = params?.id as string;
  const { canApprove } = useAuth();
  const [feedback, setFeedback] = useState<string | null>(null);
  const [historyRef, setHistoryRef] = useState<string>("");
  const [receiptOpen, setReceiptOpen] = useState(false);

  const { data: job, isLoading: isJobLoading, error: jobError } = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => fetchJob(jobId),
    enabled: !!jobId,
  });

  const { data: summaryData } = useQuery({
    queryKey: ["job-summary", jobId],
    queryFn: () => fetchJobSummary(jobId),
    enabled: !!jobId,
  });

  const { data: items = [] } = useQuery({
    queryKey: ["job-items", jobId],
    queryFn: () => fetchJobItems(jobId),
    enabled: !!jobId,
  });

  const { data: issues = [] } = useQuery({
    queryKey: ["job-issues", jobId],
    queryFn: () => fetchJobIssues(jobId),
    enabled: !!jobId,
  });

  const { data: filesData } = useQuery({
    queryKey: ["job-files", jobId],
    queryFn: () => listJobFiles(jobId),
    enabled: !!jobId,
  });

  const { data: receipt } = useQuery({
    queryKey: ["job-receipt", jobId],
    queryFn: () => fetchReceipt(jobId),
    enabled: !!jobId && receiptOpen,
  });

  const { data: priceHistory } = useQuery({
    queryKey: ["price-history", historyRef],
    queryFn: () => fetchPriceHistory(historyRef),
    enabled: !!historyRef && canApprove,
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["job", jobId] });
    queryClient.invalidateQueries({ queryKey: ["job-summary", jobId] });
    queryClient.invalidateQueries({ queryKey: ["job-files", jobId] });
  };

  const approveMutation = useMutation({
    mutationFn: () => approveJob(jobId, "Aprovado via interface web Cotarco"),
    onSuccess: () => {
      setFeedback("Processamento aprovado. Pode executar a exportação.");
      invalidate();
    },
    onError: (err: Error) => setFeedback(err.message),
  });

  const rejectMutation = useMutation({
    mutationFn: () => rejectJob(jobId, "Rejeitado via interface web Cotarco"),
    onSuccess: () => {
      setFeedback("Lote rejeitado e cancelado.");
      invalidate();
    },
    onError: (err: Error) => setFeedback(err.message),
  });

  const processMutation = useMutation({
    mutationFn: () => processJob(jobId),
    onSuccess: () => {
      setFeedback("Exportação concluída. Ficheiros OUTPUT e LOG disponíveis.");
      invalidate();
      setReceiptOpen(true);
    },
    onError: (err: Error) => setFeedback(err.message),
  });

  const summary = summaryData?.summary || job?.summary || {
    total: 0,
    updated: 0,
    new: 0,
    ignored: 0,
    blocked: 0,
  };

  const isDryRun = Boolean(job?.options?.dry_run || summary?.dry_run);
  const status = String(job?.status || "UPLOADED");
  const canApproveNow = Boolean(canApprove && status === "READY_FOR_REVIEW" && !isDryRun);
  const canProcessNow = Boolean(canApprove && status === "APPROVED" && !isDryRun);
  const canRejectNow = Boolean(
    canApprove && (status === "READY_FOR_REVIEW" || status === "NEEDS_CORRECTION")
  );
  const approveDisabled = !canApproveNow || approveMutation.isPending || ["COMPLETED", "CANCELLED", "FAILED"].includes(status);
  const approveLabel =
    status === "COMPLETED" ? "Concluído" : status === "APPROVED" ? "Aprovado" : "Aprovar Processamento";

  const outputFiles = useMemo(
    () => (filesData?.items || []).filter((f) => f.kind === "OUTPUT" || f.kind === "LOG"),
    [filesData]
  );
  const inputFile = (filesData?.items || []).find((f) => f.kind === "INPUT");

  const blockedItems = items.filter((i) => i.decision === "BLOCKED");

  if (isJobLoading) {
    return (
      <div className="container max-w-7xl mx-auto px-4 py-8 text-sm text-slateSecondary">
        A carregar processamento…
      </div>
    );
  }

  if (jobError || !job) {
    return (
      <div className="container max-w-7xl mx-auto px-4 py-8 space-y-4">
        <Link href="/" className="text-xs text-brand font-semibold">
          ← Voltar
        </Link>
        <p className="text-sm text-error">
          {(jobError as Error)?.message || "Processamento não encontrado."}
        </p>
      </div>
    );
  }

  return (
    <div className="container max-w-7xl mx-auto px-4 py-8 space-y-6">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs text-slateSecondary hover:text-ink font-semibold"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        Voltar aos Processamentos
      </Link>

      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 border-b border-border pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-2xl font-bold tracking-tight text-ink font-mono">
              #{String(job.job_number || 0).padStart(6, "0")}
            </h1>
            <Badge variant="warning" className="gap-1 font-semibold text-xs">
              <Clock className="h-3 w-3" />
              {status}
            </Badge>
            {isDryRun && (
              <Badge variant="info" className="text-xs">
                DRY-RUN
              </Badge>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-3 text-xs text-slateSecondary pt-0.5">
            <span>
              Fonte: <strong className="text-ink">{job.source_system || "—"}</strong>
            </span>
            <span>•</span>
            <span>
              Data: <strong className="text-ink">{formatDate(job.created_at)}</strong>
            </span>
            <span>•</span>
            <span>
              Ficheiro:{" "}
              <strong className="text-ink">
                {inputFile?.original_name || job.description || "—"}
              </strong>
            </span>
          </div>
          {job.description && (
            <p className="text-xs text-slateSecondary">{job.description}</p>
          )}
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="gap-1.5"
            onClick={() => setReceiptOpen(true)}
          >
            <Receipt className="h-3.5 w-3.5" />
            Recibo
          </Button>
          <div className="flex items-center gap-1.5 px-3 py-1 rounded bg-canvas border border-border text-xs text-slateSecondary">
            <ShieldCheck className="h-4 w-4 text-emerald-600" />
            <span>
              Perfil: <strong>{String(summary?.profile_code || "—")}</strong>
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {[
          { label: "Total Analisados", value: summary.total, hint: "linhas origem" },
          { label: "Atualizações", value: summary.updated, hint: "preço/stock" },
          { label: "Novos Produtos", value: summary.new, hint: "stock ok" },
          { label: "Ignorados", value: summary.ignored, hint: "regras stock" },
          { label: "Bloqueados", value: summary.blocked, hint: "Price Guard" },
        ].map((m) => (
          <Card key={m.label} className="p-4 space-y-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slateSecondary block">
              {m.label}
            </span>
            <div className="text-2xl font-bold font-mono tabular-nums text-ink">
              {formatNumber(Number(m.value ?? 0))}
            </div>
            <span className="text-[10px] text-slateSecondary">{m.hint}</span>
          </Card>
        ))}
      </div>

      {blockedItems.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-1.5">
              <AlertOctagon className="h-4 w-4 text-error" />
              Porque foi bloqueado ({blockedItems.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {blockedItems.slice(0, 12).map((item) => (
              <div
                key={item.id}
                className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 text-xs border border-red-100 bg-red-50/40 rounded p-3"
              >
                <div>
                  <span className="font-mono font-bold text-ink">
                    {item.reference_normalized}
                  </span>
                  <p className="text-slateSecondary mt-0.5">
                    {explainBlockCode(item.decision_code)}
                    {item.price_variation_pct != null && (
                      <> · variação {item.price_variation_pct.toFixed(1)}%</>
                    )}
                  </p>
                </div>
                {canApprove && (
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    className="text-xs"
                    onClick={() => setHistoryRef(item.reference_normalized)}
                  >
                    Histórico de preço
                  </Button>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {historyRef && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">
              Histórico de preços · {historyRef}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs space-y-1">
            {(priceHistory?.items || []).length === 0 && (
              <p className="text-slateSecondary">Sem histórico aceite ainda.</p>
            )}
            {(priceHistory?.items || []).map((h) => (
              <div key={String(h.id)} className="flex justify-between border-b border-border py-1 font-mono">
                <span>{String(h.recorded_at || "")}</span>
                <span>
                  {String(h.old_price ?? "—")} → {String(h.new_price ?? "—")} ({String(h.change_type)})
                </span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-ink flex items-center gap-1.5">
            <AlertOctagon className="h-4 w-4 text-error" />
            Alertas e Bloqueios ({issues.length})
          </h2>
        </div>
        <ValidationIssueList issues={issues} />
      </div>

      <div className="space-y-3 pt-2">
        <div>
          <h2 className="text-sm font-bold text-ink">
            Diferencial de Preços e Stocks
          </h2>
          <p className="text-xs text-slateSecondary">
            Comparação do ficheiro submetido contra o catálogo / histórico aceite.
          </p>
        </div>
        <DiffViewer items={items} />
      </div>

      {outputFiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Ficheiros de exportação</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {outputFiles.map((f) => (
              <Button
                key={f.id}
                type="button"
                variant="outline"
                size="sm"
                className="gap-1.5"
                onClick={() => downloadJobFile(jobId, f.id, f.original_name)}
              >
                <Download className="h-3.5 w-3.5" />
                {f.kind}: {f.original_name}
              </Button>
            ))}
          </CardContent>
        </Card>
      )}

      {receiptOpen && receipt && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Recibo de processamento</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-[11px] font-mono bg-canvas border border-border rounded p-3 overflow-auto max-h-64">
              {JSON.stringify(receipt, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}

      {feedback && (
        <div className="flex items-center gap-2 p-4 rounded-md border border-emerald-300 bg-emerald-50 text-emerald-900 text-xs font-semibold">
          <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
          <span>{feedback}</span>
        </div>
      )}

      <div className="sticky bottom-0 z-30 -mx-4 -mb-8 px-6 py-4 bg-surface border-t border-border shadow-lg flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link href="/">
            <Button type="button" variant="outline" size="sm">
              Voltar
            </Button>
          </Link>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            disabled={!canRejectNow || rejectMutation.isPending}
            onClick={() => rejectMutation.mutate()}
            className="text-slateSecondary hover:text-error gap-1"
          >
            <XCircle className="h-4 w-4" />
            Rejeitar Lote
          </Button>
        </div>

        <div className="flex items-center gap-4">
          {!canApprove ? (
            <div className="flex items-center gap-2 text-xs text-amber-800 bg-amber-50 px-3 py-1.5 rounded border border-amber-200">
              <ShieldAlert className="h-4 w-4 text-amber-600 shrink-0" />
              <span>
                <strong>Comercial:</strong> apenas Operador/Admin pode aprovar.
              </span>
            </div>
          ) : isDryRun ? (
            <div className="text-xs text-amber-800 bg-amber-50 px-3 py-1.5 rounded border border-amber-200">
              Dry-run: aprovação e exportação desativadas.
            </div>
          ) : null}

          {canProcessNow ? (
            <Button
              type="button"
              disabled={processMutation.isPending}
              onClick={() => processMutation.mutate()}
              className="gap-2 font-bold px-6 min-w-[200px]"
            >
              {processMutation.isPending ? (
                "A exportar…"
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Executar Exportação
                </>
              )}
            </Button>
          ) : (
            <Button
              type="button"
              disabled={approveDisabled}
              onClick={() => approveMutation.mutate()}
              className="gap-2 font-bold px-6 min-w-[200px]"
            >
              {approveMutation.isPending ? (
                "A aprovar…"
              ) : (
                <>
                  {approveLabel === "Aprovar Processamento" ? (
                    <FileCheck2 className="h-4 w-4" />
                  ) : (
                    <CheckCircle2 className="h-4 w-4" />
                  )}
                  {approveLabel}
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
