"use client";

import React, { useState, useRef } from "react";
import { UploadCloud, FileCheck, X, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface UploadZoneProps {
  onFileSelect: (file: File | null) => void;
  selectedFile: File | null;
}

export function UploadZone({ onFileSelect, selectedFile }: UploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateAndSetFile = (file: File) => {
    setError(null);
    if (!file.name.endsWith(".xlsx") && !file.name.endsWith(".xls")) {
      setError("Formato inválido. Por favor envie ficheiro .xlsx ou .xls.");
      return;
    }
    const maxSize = 25 * 1024 * 1024; // 25MB
    if (file.size > maxSize) {
      setError("O ficheiro excede o limite máximo permitido de 25 MB.");
      return;
    }
    onFileSelect(file);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const removeFile = () => {
    onFileSelect(null);
    setError(null);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-3">
      <input
        ref={inputRef}
        type="file"
        accept=".xlsx,.xls"
        className="sr-only"
        onChange={handleChange}
      />

      {!selectedFile ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragOver(true);
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`flex flex-col items-center justify-center rounded-md border-2 border-dashed p-8 text-center cursor-pointer transition-colors ${
            isDragOver
              ? "border-brand bg-brand-subtle/50"
              : "border-slateSecondary/40 hover:border-slateSecondary bg-canvas/40 hover:bg-canvas"
          }`}
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-surface border border-border mb-3 shadow-sm">
            <UploadCloud className="h-6 w-6 text-brand" />
          </div>
          <span className="text-sm font-semibold text-ink">
            Arraste a tabela .xlsx aqui ou{" "}
            <span className="text-brand hover:underline">escolha no computador</span>
          </span>
          <span className="text-xs text-slateSecondary mt-1">
            Ficheiros suportados: .xlsx, .xls • Limite: até 25 MB
          </span>
          <div className="mt-4 flex items-center gap-2 text-[11px] text-slateSecondary/80 bg-surface px-3 py-1 rounded border border-border">
            <span>Colunas requeridas: Referência, Preço, Stock</span>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-between rounded-md border border-emerald-200 bg-emerald-50/50 p-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded bg-emerald-100 text-emerald-700">
              <FileCheck className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold text-ink">{selectedFile.name}</span>
              <span className="text-xs text-slateSecondary">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Pronto para validação
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => inputRef.current?.click()}
            >
              Substituir
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={removeFile}
              className="text-slateSecondary hover:text-error"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 text-xs text-error font-medium p-2.5 rounded bg-red-50 border border-red-200">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
