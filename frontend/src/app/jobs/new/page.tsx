"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { fetchProfiles, createJob, uploadJobFile, validateJob } from "@/lib/api";
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
} from "lucide-react";

export default function NewJobPage() {
  const router = useRouter();

  const [selectedProfileId, setSelectedProfileId] = useState("");
  const [sourceSystem, setSourceSystem] = useState("SAMSUNG");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [catalogFile, setCatalogFile] = useState<File | null>(null);
  const [dryRun, setDryRun] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { data: profilesData } = useQuery({
    queryKey: ["profiles"],
    queryFn: fetchProfiles,
  });

  const profiles = profilesData?.items ?? [];
  const currentProfile = profiles.find((p) => p.id === selectedProfileId) || profiles[0];
  const threshold =
    currentProfile?.config?.price_guard_threshold_pct ??
    (currentProfile?.config?.price_variation_threshold
      ? Number(currentProfile.config.price_variation_threshold) * 100
      : 30);
  const minStock =
    currentProfile?.config?.new_product_min_stock ??
    currentProfile?.config?.stock_min_activation ??
    3;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setErrorMessage("Por favor selecione um ficheiro Excel (.xlsx) para validar.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const profileId = selectedProfileId || profiles[0]?.id;
      if (!profileId) {
        throw new Error("Nenhum perfil comercial disponível. Contacte o administrador.");
      }
      const created = await createJob({
        profile_id: profileId,
        source_system: sourceSystem,
        description: description || `Lote ${file.name}`,
        options: { dry_run: dryRun },
      });
      await uploadJobFile(created.id, file, "INPUT");
      if (catalogFile) {
        await uploadJobFile(created.id, catalogFile, "CATALOG");
      }
      await validateJob(created.id, dryRun);
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
            Price Guard Pronto
          </div>
        </div>
      </div>

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
          <span className="text-xs font-semibold text-slateSecondary">Aprovação & Exportação</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Configuração da Tabela</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-ink">
                  Perfil Comercial Alvo <span className="text-error">*</span>
                </label>
                <Select
                  value={selectedProfileId || profiles[0]?.id || ""}
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

              <label className="flex items-center gap-2 text-xs text-ink cursor-pointer">
                <input
                  type="checkbox"
                  checked={dryRun}
                  onChange={(e) => setDryRun(e.target.checked)}
                  className="rounded border-border"
                />
                <span>
                  <strong>Dry-run</strong> — validar e ver diff sem permitir aprovação/exportação
                </span>
              </label>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center justify-between">
                <span>Ficheiro Excel de origem (.xlsx)</span>
                <span className="text-[11px] font-normal text-slateSecondary">
                  O original nunca é sobrescrito
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <UploadZone onFileSelect={setFile} selectedFile={file} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">
                Catálogo atual (opcional)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-[11px] text-slateSecondary">
                Sem catálogo, todos os SKUs válidos são tratados como novos. Use o fixture
                em <code className="font-mono">fixtures/excel/sample_catalog.xlsx</code>.
              </p>
              <UploadZone onFileSelect={setCatalogFile} selectedFile={catalogFile} />
            </CardContent>
          </Card>

          {errorMessage && (
            <div className="flex items-center gap-2 p-3 text-xs text-error bg-red-50 rounded border border-red-200">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

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
                  A validar…
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
                  {currentProfile?.name || "—"}
                </span>
                <div className="space-y-1 text-slateSecondary">
                  <div className="flex justify-between">
                    <span>Limiar Price Guard:</span>
                    <span className="font-bold text-ink">±{threshold}% variação</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Stock Mínimo (Novo):</span>
                    <span className="font-bold text-ink">≥ {String(minStock)} unidades</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Preço Zero:</span>
                    <span className="font-bold text-error">Bloqueante</span>
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-border">
                <a href="/fixtures/sample_input_samsung.xlsx" download>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="w-full gap-1.5 text-xs text-slateSecondary justify-center"
                  >
                    <Download className="h-3.5 w-3.5" />
                    Descarregar Modelo .xlsx
                  </Button>
                </a>
              </div>
            </CardContent>
          </Card>
        </div>
      </form>
    </div>
  );
}
