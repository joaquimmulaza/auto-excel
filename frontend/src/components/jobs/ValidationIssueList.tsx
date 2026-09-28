"use client";

import React, { useState } from "react";
import { ValidationIssueResponse, AIAnomalyExplanation } from "@/types";
import { explainIssueWithAi } from "@/lib/api";
import { AlertCircle, AlertTriangle, Info, Sparkles, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";

interface ValidationIssueListProps {
  issues: ValidationIssueResponse[];
}

export function ValidationIssueList({ issues }: ValidationIssueListProps) {
  const [selectedIssue, setSelectedIssue] = useState<ValidationIssueResponse | null>(null);
  const [isAiExplaining, setIsAiExplaining] = useState(false);
  const [aiExplanation, setAiExplanation] = useState<AIAnomalyExplanation | null>(null);
  const [aiIsRealResponse, setAiIsRealResponse] = useState(true);

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "BLOCKER":
        return <Badge variant="destructive">Bloqueio</Badge>;
      case "ERROR":
        return <Badge variant="destructive">Erro</Badge>;
      case "WARNING":
        return <Badge variant="warning">Aviso</Badge>;
      default:
        return <Badge variant="info">Info</Badge>;
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "BLOCKER":
      case "ERROR":
        return <AlertCircle className="h-4 w-4 text-error" />;
      case "WARNING":
        return <AlertTriangle className="h-4 w-4 text-warning" />;
      default:
        return <Info className="h-4 w-4 text-info" />;
    }
  };

  const handleExplainWithAi = async (issue: ValidationIssueResponse) => {
    setSelectedIssue(issue);
    setIsAiExplaining(true);
    setAiExplanation(null);
    setAiIsRealResponse(true);
    const result = await explainIssueWithAi(issue.job_id, {
      issue_code: issue.code,
      issue_message: issue.message,
      severity: issue.severity,
    });
    setAiExplanation(result.data);
    setAiIsRealResponse(!result.fallback_used);
    setIsAiExplaining(false);
  };


  if (issues.length === 0) {
    return (
      <div className="flex items-center gap-3 p-4 rounded-md border border-emerald-200 bg-emerald-50/60 text-emerald-800">
        <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
        <div className="text-xs">
          <span className="font-bold">Nenhum problema detectado.</span> Todas as
          regras de integridade e limiares de Price Guard foram validados com
          sucesso.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2.5">
      {issues.map((issue) => (
        <div
          key={issue.id}
          className={`flex items-start justify-between gap-3 p-3.5 rounded-md border ${
            issue.severity === "BLOCKER" || issue.severity === "ERROR"
              ? "border-red-300 bg-red-50/50"
              : "border-amber-300 bg-amber-50/50"
          }`}
        >
          <div className="flex items-start gap-2.5">
            <div className="mt-0.5">{getSeverityIcon(issue.severity)}</div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-ink">
                  {issue.code}
                </span>
                {getSeverityBadge(issue.severity)}
                {issue.row_number && (
                  <span className="text-[11px] text-slateSecondary font-mono">
                    Linha {issue.row_number}
                  </span>
                )}
              </div>
              <p className="text-xs text-ink/90 leading-relaxed">
                {issue.message}
              </p>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => handleExplainWithAi(issue)}
            className="shrink-0 gap-1.5 text-xs border-border bg-surface hover:bg-canvas font-semibold shadow-xs"
          >
            <Sparkles className="h-3.5 w-3.5 text-brand" />
            Explicar com IA
          </Button>
        </div>
      ))}

      {/* AI Explanation Dialog */}
      <Dialog
        open={!!selectedIssue}
        onOpenChange={(open) => !open && setSelectedIssue(null)}
      >
        <DialogHeader>
          <div className="flex items-center gap-2 text-brand">
            <Sparkles className="h-5 w-5" />
            <DialogTitle>Diagnóstico Assistivo Gemini</DialogTitle>
          </div>
          <DialogDescription>
            Interpretação e sugestão operacional para anomalia comercial
          </DialogDescription>
        </DialogHeader>

        {selectedIssue && (
          <div className="space-y-4 my-2 text-xs">
            <div className="p-3 bg-canvas rounded border border-border">
              <span className="font-semibold text-slateSecondary uppercase tracking-wider text-[10px] block mb-1">
                Problema Selecionado:
              </span>
              <div className="font-mono font-bold text-ink">{selectedIssue.code}</div>
              <div className="text-slateSecondary mt-0.5">{selectedIssue.message}</div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-ink block">
                  Parecer de IA (Gemini Commercial Assistant):
                </span>
                {!isAiExplaining && aiExplanation && !aiIsRealResponse && (
                  <span className="text-[10px] text-slateSecondary bg-canvas border border-border rounded px-1.5 py-0.5">
                    Análise local · IA indisponível
                  </span>
                )}
              </div>
              {isAiExplaining ? (
                <div className="flex items-center gap-2 text-slateSecondary py-4">
                  <div className="h-4 w-4 rounded-full border-2 border-brand border-t-transparent animate-spin" />
                  <span>Analisando histórico de preços e regras do perfil...</span>
                </div>
              ) : (
                <div className="space-y-2.5 text-ink/90 leading-relaxed bg-brand-subtle/30 p-3 rounded border border-brand/20">
                  <p>
                    <strong>Causa Raiz:</strong> {aiExplanation?.likely_cause}
                  </p>
                  <p>
                    <strong>Explicação:</strong> {aiExplanation?.plain_explanation}
                  </p>
                  <p>
                    <strong>Ação Recomendada:</strong> {aiExplanation?.suggested_action}
                  </p>
                  {aiExplanation?.is_blocker && (
                    <p className="text-error font-bold">Este problema bloqueia o processamento e requer intervenção.</p>
                  )}
                  <p className="text-[11px] text-slateSecondary border-t border-border pt-2 italic">
                    Guardrail: De acordo com a governança CCM, anomalias de preço requerem revisão manual ou retificação da folha de cálculo pela equipa Comercial antes da aprovação do Operador.
                  </p>
                </div>
              )}
            </div>

          </div>
        )}

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => setSelectedIssue(null)}
          >
            Fechar
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  );
}
