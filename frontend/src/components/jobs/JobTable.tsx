"use client";

import React from "react";
import Link from "next/link";
import { JobResponse, JobStatus } from "@/types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatDate, formatNumber } from "@/lib/utils";
import { ArrowRight, FileSpreadsheet, AlertTriangle, CheckCircle, Clock } from "lucide-react";

interface JobTableProps {
  jobs: JobResponse[];
  isLoading?: boolean;
}

export function JobTable({ jobs, isLoading }: JobTableProps) {
  const getStatusBadge = (status: JobStatus) => {
    switch (status) {
      case "READY_FOR_REVIEW":
        return (
          <Badge variant="warning" className="gap-1">
            <Clock className="h-3 w-3" />
            Revisão Pronta
          </Badge>
        );
      case "COMPLETED":
        return (
          <Badge variant="success" className="gap-1">
            <CheckCircle className="h-3 w-3" />
            Concluído
          </Badge>
        );
      case "NEEDS_CORRECTION":
        return (
          <Badge variant="destructive" className="gap-1">
            <AlertTriangle className="h-3 w-3" />
            Correção
          </Badge>
        );
      case "VALIDATING":
        return (
          <Badge variant="info" className="gap-1 animate-pulse">
            Validando
          </Badge>
        );
      case "APPROVED":
        return (
          <Badge variant="success" className="gap-1">
            Aprovado
          </Badge>
        );
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-2 p-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-12 w-full bg-canvas animate-pulse rounded border border-border" />
        ))}
      </div>
    );
  }

  if (jobs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center bg-surface rounded-md border border-border">
        <FileSpreadsheet className="h-10 w-10 text-slateSecondary mb-3 opacity-60" />
        <h4 className="text-sm font-semibold text-ink">Nenhum processamento encontrado</h4>
        <p className="text-xs text-slateSecondary max-w-sm mt-1 mb-4">
          Submeta uma nova tabela de preços e stock para iniciar a validação automatizada.
        </p>
        <Link href="/jobs/new">
          <Button size="sm">Novo Processamento</Button>
        </Link>
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-24">Job #</TableHead>
          <TableHead>Perfil Comercial</TableHead>
          <TableHead>Fonte</TableHead>
          <TableHead className="text-right">Itens</TableHead>
          <TableHead>Estado</TableHead>
          <TableHead>Criado em</TableHead>
          <TableHead className="text-right">Ação</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {jobs.map((job) => {
          const totalItems = job.summary?.total ?? 0;
          return (
            <TableRow key={job.id} className="cursor-pointer group">
              <TableCell className="font-mono font-bold text-xs text-ink">
                #{String(job.job_number || 184).padStart(6, "0")}
              </TableCell>
              <TableCell>
                <div className="font-medium text-xs text-ink">
                  {job.profile_id.includes("1111")
                    ? "Marketplace Mano"
                    : job.profile_id.includes("2222")
                    ? "Loja Online Cotarco"
                    : "BFA Wholesale"}
                </div>
                <div className="text-[11px] text-slateSecondary truncate max-w-xs">
                  {job.description || "Sem descrição"}
                </div>
              </TableCell>
              <TableCell className="text-xs font-medium text-slateSecondary">
                {job.source_system || "SAMSUNG"}
              </TableCell>
              <TableCell className="text-right font-mono text-xs tabular-nums text-ink">
                {formatNumber(totalItems)}
              </TableCell>
              <TableCell>{getStatusBadge(job.status)}</TableCell>
              <TableCell className="text-xs text-slateSecondary font-mono tabular-nums">
                {formatDate(job.created_at)}
              </TableCell>
              <TableCell className="text-right">
                <Link href={`/jobs/${job.id}`}>
                  <Button
                    variant="outline"
                    size="sm"
                    className="gap-1 text-xs group-hover:border-brand group-hover:text-brand"
                  >
                    Ver Diff
                    <ArrowRight className="h-3 w-3" />
                  </Button>
                </Link>
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
