"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchProfiles, updateProfile } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ArrowLeft } from "lucide-react";

export default function ProfilesPage() {
  const { isAdmin } = useAuth();
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["profiles"],
    queryFn: fetchProfiles,
    enabled: isAdmin,
  });
  const [edits, setEdits] = useState<Record<string, { threshold: string; minStock: string }>>({});
  const [message, setMessage] = useState<string | null>(null);

  const saveMutation = useMutation({
    mutationFn: async (profileId: string) => {
      const profile = data?.items.find((p) => p.id === profileId);
      const edit = edits[profileId];
      if (!profile || !edit) return;
      const threshold = Number(edit.threshold);
      const minStock = Number(edit.minStock);
      return updateProfile(profileId, {
        config: {
          ...profile.config,
          price_guard_threshold_pct: threshold,
          price_variation_threshold: threshold / 100,
          new_product_min_stock: minStock,
          stock_min_activation: minStock,
        },
      });
    },
    onSuccess: () => {
      setMessage("Perfil atualizado.");
      queryClient.invalidateQueries({ queryKey: ["profiles"] });
    },
    onError: (err: Error) => setMessage(err.message),
  });

  if (!isAdmin) {
    return (
      <div className="container max-w-4xl mx-auto px-4 py-8 text-sm text-slateSecondary">
        Apenas Admin pode configurar perfis comerciais.
      </div>
    );
  }

  const profiles = data?.items ?? [];

  return (
    <div className="container max-w-4xl mx-auto px-4 py-8 space-y-6">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs text-slateSecondary hover:text-ink font-semibold"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        Voltar
      </Link>
      <div>
        <h1 className="text-2xl font-bold text-ink">Perfis Comerciais</h1>
        <p className="text-xs text-slateSecondary mt-1">
          Ajuste limiares do Price Guard e stock mínimo sem código.
        </p>
      </div>
      {message && <p className="text-xs text-emerald-800 bg-emerald-50 border border-emerald-200 rounded p-2">{message}</p>}
      {isLoading && <p className="text-xs text-slateSecondary">A carregar…</p>}
      <div className="space-y-4">
        {profiles.map((p) => {
          const threshold =
            edits[p.id]?.threshold ??
            String(p.config.price_guard_threshold_pct ?? 30);
          const minStock =
            edits[p.id]?.minStock ??
            String(p.config.new_product_min_stock ?? p.config.stock_min_activation ?? 3);
          return (
            <Card key={p.id}>
              <CardHeader>
                <CardTitle className="text-sm">
                  {p.code} · {p.name}
                </CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-end">
                <div className="space-y-1">
                  <label className="text-[11px] font-bold">Limiar variação %</label>
                  <Input
                    value={threshold}
                    onChange={(e) =>
                      setEdits((prev) => ({
                        ...prev,
                        [p.id]: { threshold: e.target.value, minStock },
                      }))
                    }
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[11px] font-bold">Stock mínimo novo</label>
                  <Input
                    value={minStock}
                    onChange={(e) =>
                      setEdits((prev) => ({
                        ...prev,
                        [p.id]: { threshold, minStock: e.target.value },
                      }))
                    }
                  />
                </div>
                <Button
                  type="button"
                  size="sm"
                  disabled={saveMutation.isPending}
                  onClick={() => saveMutation.mutate(p.id)}
                >
                  Guardar
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
