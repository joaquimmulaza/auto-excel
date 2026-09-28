"use client";

import React, { useState, useMemo } from "react";
import { JobItemResponse } from "@/types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { Search, ShieldAlert, ArrowUpRight, ArrowDownRight, Minus, AlertOctagon } from "lucide-react";

interface DiffViewerProps {
  items: JobItemResponse[];
}

type FilterType = "ALL" | "UPDATE" | "NEW" | "IGNORED" | "BLOCKED";

export function DiffViewer({ items }: DiffViewerProps) {
  const [activeFilter, setActiveFilter] = useState<FilterType>("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  const counts = useMemo(() => {
    return {
      ALL: items.length,
      UPDATE: items.filter((i) => i.decision === "UPDATE").length,
      NEW: items.filter((i) => i.decision === "NEW").length,
      IGNORED: items.filter((i) => i.decision === "IGNORED").length,
      BLOCKED: items.filter((i) => i.decision === "BLOCKED").length,
    };
  }, [items]);

  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      // Type filter
      if (activeFilter !== "ALL" && item.decision !== activeFilter) {
        return false;
      }
      // Search query
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const refMatch =
          item.reference_normalized.toLowerCase().includes(query) ||
          item.reference_original.toLowerCase().includes(query);
        return refMatch;
      }
      return true;
    });
  }, [items, activeFilter, searchQuery]);

  const renderDecisionBadge = (decision: string) => {
    switch (decision) {
      case "UPDATE":
        return <Badge variant="success">Update</Badge>;
      case "NEW":
        return <Badge variant="info">Novo</Badge>;
      case "IGNORED":
        return <Badge variant="secondary">Ignorado</Badge>;
      case "BLOCKED":
        return (
          <Badge variant="priceGuard" className="gap-1">
            <AlertOctagon className="h-3 w-3 text-error" />
            Bloqueado
          </Badge>
        );
      default:
        return <Badge variant="outline">{decision}</Badge>;
    }
  };

  const renderVariationBadge = (variation: number | null | undefined, decision: string) => {
    if (decision === "NEW") {
      return (
        <span className="inline-flex items-center text-xs font-mono font-medium text-blue-700 bg-blue-50 px-2 py-0.5 rounded">
          Novo Item
        </span>
      );
    }
    if (variation === null || variation === undefined) {
      return <span className="text-slateSecondary">—</span>;
    }
    if (decision === "BLOCKED" || Math.abs(variation) >= 30) {
      return (
        <span className="inline-flex items-center gap-0.5 text-xs font-mono font-bold text-red-700 bg-red-100 px-2 py-0.5 rounded">
          <ShieldAlert className="h-3 w-3" />
          {formatPercent(variation)}
        </span>
      );
    }
    if (variation > 0) {
      return (
        <span className="inline-flex items-center gap-0.5 text-xs font-mono font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
          <ArrowUpRight className="h-3 w-3" />
          {formatPercent(variation)}
        </span>
      );
    }
    if (variation < 0) {
      return (
        <span className="inline-flex items-center gap-0.5 text-xs font-mono font-medium text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
          <ArrowDownRight className="h-3 w-3" />
          {formatPercent(variation)}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-0.5 text-xs font-mono text-slateSecondary px-2 py-0.5">
        <Minus className="h-3 w-3" />
        0.0%
      </span>
    );
  };

  return (
    <div className="space-y-3">
      {/* Controls Bar: Filter Pills + Search */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          <button
            type="button"
            onClick={() => setActiveFilter("ALL")}
            className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
              activeFilter === "ALL"
                ? "bg-ink text-white shadow-xs"
                : "bg-surface border border-border text-slateSecondary hover:text-ink"
            }`}
          >
            Todos ({counts.ALL})
          </button>
          <button
            type="button"
            onClick={() => setActiveFilter("UPDATE")}
            className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
              activeFilter === "UPDATE"
                ? "bg-emerald-700 text-white shadow-xs"
                : "bg-surface border border-border text-slateSecondary hover:text-ink"
            }`}
          >
            Atualizações ({counts.UPDATE})
          </button>
          <button
            type="button"
            onClick={() => setActiveFilter("NEW")}
            className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
              activeFilter === "NEW"
                ? "bg-blue-700 text-white shadow-xs"
                : "bg-surface border border-border text-slateSecondary hover:text-ink"
            }`}
          >
            Novos ({counts.NEW})
          </button>
          <button
            type="button"
            onClick={() => setActiveFilter("IGNORED")}
            className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
              activeFilter === "IGNORED"
                ? "bg-slate-700 text-white shadow-xs"
                : "bg-surface border border-border text-slateSecondary hover:text-ink"
            }`}
          >
            Ignorados ({counts.IGNORED})
          </button>
          <button
            type="button"
            onClick={() => setActiveFilter("BLOCKED")}
            className={`px-3 py-1 rounded text-xs font-bold transition-all ${
              activeFilter === "BLOCKED"
                ? "bg-brand text-white shadow-xs"
                : "bg-surface border border-red-200 text-red-700 hover:bg-red-50"
            }`}
          >
            Bloqueados ({counts.BLOCKED})
          </button>
        </div>

        {/* Quick SKU search */}
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slateSecondary" />
          <Input
            placeholder="Buscar por referência / SKU..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 h-8 text-xs bg-surface"
          />
        </div>
      </div>

      {/* High Density Table */}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-44">Referência / SKU</TableHead>
            <TableHead className="text-right">Preço Atual</TableHead>
            <TableHead className="text-right">Preço Novo</TableHead>
            <TableHead className="text-center">Variação %</TableHead>
            <TableHead className="text-center">Stock (Ant → Novo)</TableHead>
            <TableHead className="text-center">Decisão</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredItems.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center py-8 text-xs text-slateSecondary">
                Nenhum produto corresponde aos filtros selecionados.
              </TableCell>
            </TableRow>
          ) : (
            filteredItems.map((item) => {
              const isBlocked = item.decision === "BLOCKED";
              return (
                <TableRow
                  key={item.id}
                  className={isBlocked ? "bg-red-50/40 hover:bg-red-50/70" : undefined}
                >
                  <TableCell>
                    <div className="font-mono text-xs font-bold text-ink">
                      {item.reference_normalized}
                    </div>
                    {item.reference_original !== item.reference_normalized && (
                      <div className="font-mono text-[10px] text-slateSecondary">
                        Orig: {item.reference_original}
                      </div>
                    )}
                  </TableCell>
                  <TableCell className="text-right font-mono text-xs tabular-nums text-slateSecondary">
                    {formatCurrency(item.old_price)}
                  </TableCell>
                  <TableCell className="text-right font-mono text-xs tabular-nums font-bold text-ink">
                    {formatCurrency(item.new_price)}
                  </TableCell>
                  <TableCell className="text-center">
                    {renderVariationBadge(item.price_variation_pct, item.decision)}
                  </TableCell>
                  <TableCell className="text-center font-mono text-xs tabular-nums">
                    {item.old_stock !== null && item.old_stock !== undefined ? (
                      <span>
                        <span className="text-slateSecondary">{item.old_stock}</span>
                        {" → "}
                        <span className="font-bold text-ink">{item.new_stock ?? 0}</span>
                      </span>
                    ) : (
                      <span className="font-bold text-ink">{item.new_stock ?? 0}</span>
                    )}
                  </TableCell>
                  <TableCell className="text-center">
                    {renderDecisionBadge(item.decision)}
                  </TableCell>
                </TableRow>
              );
            })
          )}
        </TableBody>
      </Table>
    </div>
  );
}
