"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { fetchProfiles, createJob } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { UploadZone } from "@/components/jobs/UploadZone";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import {
  ArrowLeft,
  CheckCircle2,
  ShieldCheck,
  Download,
  AlertCircle,
  FileSpreadsheet,
} from "lucide-react";

export default function NewJobPage() {
  const router = useRouter();
  const { user } = useAuth();

  const [selectedProfileId, setSelectedProfileId] = useState("");
  const [sourceSystem, setSourceSystem] = useState("SAMSUNG");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { data: profilesData } = useQuery({
    queryKey: ["profiles"],
    queryFn: fetchProfiles,
  });

  const profiles = profilesData?.items ?? [];
  const currentProfile = profiles.find((p) => p.id === selectedProfileId) || profiles[0];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setErrorMessage("Por favor selecione um ficheiro Excel (.xlsx) para validar.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const profileId = selectedProfileId || profiles[0]?.id || "11111111-1111-1111-1111-111111111111";
      const created = await createJob({
        profile_id: profileId,
        source_system: sourceSystem,
        description: description || `Lote ${file.name}`,
      });

      // Redirect to Job review page
      router.push(`/jobs/${created.id}`);
    } catch (err: unknown) {
      setErrorMessage(
        err instanceof Error ? err.message : "Erro ao criar processamento"
      );
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container max-w-5xl mx-auto px-4 py-8 space-y-8">
      {/* Header & Back link */}
      <div className="space-y-2">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-xs text-slateSecondary hover:text-ink font-semibold"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Voltar ao Dashboard
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-ink">
              Novo Processamento
            </h1>
            <p className="text-xs text-slateSecondary mt-1">
              Preparar e validar uma nova tabela comercial de preços e stock.
            </p>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 rounded bg-canvas border border-border text-xs text-slateSecondary font-mono">
            <ShieldCheck className="h-4 w-4 text-emerald-600" />
            Price Guard v2.4 Pronto
          </div>
        </div>
      </div>

      {/* Stepper */}
      <div className="grid grid-cols-3 gap-2 border-b border-border pb-4">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-brand text-white text-xs font-bold">
            1
          </div>
          <span className="text-xs font-bold text-brand">Configuração & Ficheiro</span>
        </div>
        <div className="flex items-center gap-2 opacity-50">
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-slateSecondary text-white text-xs font-bold">
            2
          </div>
          <span className="text-xs font-semibold text-slateSecondary">Validação & Diff</span>
        </div>
        <div className="flex items-center gap-2 opacity-50">
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-slateSecondary text-white text-xs font-bold">
            3
          </div>
          <span className="text-xs font-semibold text-slateSecondary">Aprovação & Sincronização</span>
        </div>
      </div>

      {/* Form Grid */}
      <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left 2 Cols: Inputs and Upload */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Configuração da Tabela</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Profile selection */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-ink">
                  Perfil Comercial Alvo <span className="text-error">*</span>
                </label>
                <Select
                  value={selectedProfileId || profiles[0]?.id}
                  onChange={(e) => setSelectedProfileId(e.target.value)}
                  className="bg-surface"
                >
                  {profiles.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.type})
                    </option>
                  ))}
                </Select>
                {currentProfile && (
                  <p className="text-[11px] text-slateSecondary mt-1">
                    {currentProfile.description}
                  </p>
                )}
              </div>

              {/* Source system */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-ink">
                  Fonte de Dados <span className="text-error">*</span>
                </label>
                <Select
                  value={sourceSystem}
                  onChange={(e) => setSourceSystem(e.target.value)}
                  className="bg-surface"
                >
                  <option value="SAMSUNG">Samsung Catálogo Oficial</option>
                  <option value="LG">LG Direct API Feed</option>
                  <option value="PHILIPS">Philips Global Catalog</option>
                  <option value="FORNECEDOR">Fornecedor Externo / Revendedor</option>
                </Select>
              </div>

              {/* Description */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-ink">
                  Descrição ou Notas do Lote (Opcional)
                </label>
                <Input
                  placeholder="Ex: Tabela de preços de Setembro 2026 - Linha Branca..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="bg-surface"
                />
              </div>
            </CardContent>
          </Card>

          {/* File Upload Section */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center justify-between">
                <span>Ficheiro Excel (.xlsx)</span>
                <span className="text-[11px] font-normal text-slateSecondary">
                  O original nunca é sobrescrito
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <UploadZone onFileSelect={setFile} selectedFile={file} />
            </CardContent>
          </Card>

          {errorMessage && (
            <div className="flex items-center gap-2 p-3 text-xs text-error bg-red-50 rounded border border-red-200">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Bottom Action Footer */}
          <div className="flex items-center justify-between pt-2">
            <Link href="/">
              <Button type="button" variant="outline" size="sm">
                Cancelar
              </Button>
            </Link>
            <Button
              type="submit"
              disabled={isSubmitting || !file}
              className="gap-2 font-bold min-w-[160px]"
            >
              {isSubmitting ? (
                <>
                  <div className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
                  Validando Ficheiro...
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-4 w-4" />
                  Validar Ficheiro
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Right 1 Col: Guidelines & Profile Info */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-xs uppercase tracking-wider text-slateSecondary font-bold">
                Regras Ativas do Perfil
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="p-3 rounded bg-canvas border border-border space-y-2">
                <span className="font-bold text-ink block">
                  {currentProfile?.name || "Marketplace Mano"}
                </span>
                <div className="space-y-1 text-slateSecondary">
                  <div className="flex justify-between">
                    <span>Limiar Price Guard:</span>
                    <span className="font-bold text-ink">±30% variação</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Stock Mínimo (Novo):</span>
                    <span className="font-bold text-ink">≥ 3 unidades</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Preço Zero:</span>
                    <span className="font-bold text-error">Bloqueante</span>
                  </div>
                </div>
              </div>

              <div className="space-y-1.5 pt-1">
                <span className="font-bold text-ink">Checklist de Submissão:</span>
                <ul className="space-y-1 text-slateSecondary list-disc list-inside text-[11px] leading-relaxed">
                  <li>Colunas identificadas automaticamente.</li>
                  <li>Normalização de acentos e códigos.</li>
                  <li>Deteção de anomalias sem bloquear processo.</li>
                </ul>
              </div>

              <div className="pt-2 border-t border-border">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="w-full gap-1.5 text-xs text-slateSecondary justify-center"
                  onClick={() => alert("O download de modelos de tabela estará disponível na Fase 07.")}
                >
                  <Download className="h-3.5 w-3.5" />
                  Descarregar Modelo .xlsx
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </form>
    </div>
  );
}
